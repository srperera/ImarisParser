import os
import glob
import numpy as np
from tqdm import tqdm
from typing import List, Tuple
from utils.utils import get_valid_filaments
from imaris.exceptions import NoFilamentsException
from parsers.filament_parser import FilamentParserDistributed
from concurrent.futures import ProcessPoolExecutor, as_completed


###############################################################################################
###############################################################################################
def run_filament_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    filament_ids: Tuple[int] = None,
) -> None:
    """
    Runs ALL filaments in an ims file in parallel.
    Pipeline:
        - For every file in every directory
        - Create a folder a with the same name as the filename inside save_dir provided
        - For every filament inside each file we create a remote actor
        - Once all actors are created we can use the cpu cores provided by user to
            run a fixed chunk of actors in parallel so we dont start too many instances at one
        - If no cpu_cores provided we will run all actors in parallel

    Args:
        data_dirs (List[str]): _description_
        save_dirs (List[str]): _description_
        cpu_cores (int, optional): _description_. Defaults to None.
        filament_ids (Tuple[int], optional): _description_. Defaults to None.
    """
    if filament_ids and not isinstance(filament_ids, tuple):
        raise TypeError("filament_ids must be a tuple")

    # zip data paths and save dirs
    data_paths = list(zip(data_dirs, save_dirs))

    # holds each of the individual tasks
    tasks = []

    # holds the summary for each run
    run_summary = {}

    # 1. Gather all tasks
    for data_path, save_dir in data_paths:

        # scan data path for .ims files.
        print(f"[info] -- Scanning folder: {data_path}")
        imaris_files = glob.glob(os.path.join(os.path.abspath(data_path), "*.ims"))
        run_summary[data_path] = {}

        if not imaris_files:
            print(f"[info] -- Skipping folder, no .ims files found.")
            run_summary[data_path] = None  # "NO FILES IN FOLDER"
            continue

        # loop over each of the imaris files.
        for file_path in imaris_files:
            # get filename and destination path for saving.
            filename = os.path.splitext(os.path.basename(file_path))[0]
            save_path = os.path.join(save_dir, filename)

            # create directories if needed.
            if not os.path.isdir(save_path):
                os.makedirs(save_path, exist_ok=True)

            try:
                # always check if the item is valid
                # Instructions: Modify Here If Duplicating For New Use Case
                # Create new version of get_valid_spot_tracks function
                valid_objects = get_valid_filaments(data_path=file_path)

                # if filament_ids are provided, filter valid_filament_ids
                if filament_ids:
                    # Filter to only include user-specified spot IDs
                    valid_objects = [
                        idx for idx in valid_objects if (idx + 1) in filament_ids
                    ]

                # if we have valid items in valid_filament_ids, gather items for each task.
                if len(valid_objects) > 0:
                    print(f"[info] -- Found {len(valid_objects)} spots in {filename}")
                    for idx in valid_objects:
                        # Instructions: Modify Here If Duplicating For New Use Case
                        # Depending on Class __init__ arguments can be different
                        tasks.append((file_path, idx, save_path))
                else:
                    print(
                        f"[info] -- No valid spots found in {filename} after filtering."
                    )

            # Instructions: Modify Here If Duplicating For New Use Case
            # Use Appropriate Exception.
            except NoFilamentsException:
                print(f"[info] -- File {filename} contains no spots. Skipping.")
                continue

    # 2. Execute tasks in parallel
    if not tasks:
        print("[info] -- No tasks to run. Exiting.")
        return

    print(f"\n[info] -- Found a total of {len(tasks)} tasks.")
    print(f"[info] -- Starting parallel extraction...")

    with ProcessPoolExecutor(max_workers=cpu_cores) as executor:
        # Submit tasks and track their futures
        actors = []
        for task in tasks:
            # Instructions: Modify Here If Duplicating For New Use Case
            # Use The Appropriate Class
            actor = FilamentParserDistributed(*task)
            actors.append(actor)

        # ensure we are not submitting too many jobs at a time
        # limits to at most 1 task per core.
        num_actors = len(actors)
        num_splits = np.round(num_actors / cpu_cores) if num_actors > cpu_cores else 1
        splits = np.array_split(np.asarray(actors, dtype=object), num_splits)

        for idx, split in enumerate(splits):
            future_to_task = [
                executor.submit(actor.extract_and_save, *[0]) for actor in split
            ]

            for future in tqdm(
                as_completed(future_to_task),
                total=len(split),
                colour="MAGENTA",
                ncols=80,
                desc=f"Processing split: {idx}",
            ):
                try:
                    # The result is typically None for this type of function, but we can check for exceptions
                    future.result()
                except Exception as exc:
                    print(
                        f"[error] -- Task for {task[0]} with spot ID {task[1]} generated an exception: {exc}"
                    )

    print("\n[info] -- All tasks complete.")
