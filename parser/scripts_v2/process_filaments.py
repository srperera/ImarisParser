import os
import glob
from typing import List, Tuple
from imaris.exceptions import NoFilamentsException
from utils.utils import get_valid_filaments, run_ray_actors
from parsers_v2.filament_parser import FilamentParserDistributed


"""
Notes:
    available functions:
        * run_filament_parser_parallel
        * run_filament_parser_parallel_index

    We should do all the necessary checks before creating actors
        *ie: check for valid filaments, tracks etc
        * makes everything cleaner
"""


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
    if filament_ids:
        assert isinstance(filament_ids, tuple), "filament_ids must be a tuple"
        assert len(filament_ids) > 0, "filament_ids must not be empty"

    # zip data paths and save dirs
    data_paths = list(zip(data_dirs, save_dirs))

    # summary
    run_summary = {}

    for data_path, save_dir in data_paths:
        actors = []

        # get all imaris files from current data_path directory
        imaris_files = glob.glob(os.path.join(os.path.abspath(data_path), "*.ims"))
        run_summary[data_path] = {}

        print(imaris_files)

        # if no .ims files in directory ... skip
        if len(imaris_files) == 0:
            print(f"[info] -- skipping folder no files found ")
            run_summary[data_path] = "NO FILES IN FOLDER"

        # if there are .ims files in the directory
        # there could be other .ims files like Surface, Filaments etc
        # we must only load the ones we want for filaments.
        else:
            for file_path in imaris_files:

                # get filename from path
                filename = os.path.splitext(os.path.basename(file_path))[0]
                run_summary[data_path][filename] = {}

                # create dir with same name as filename
                save_path = os.path.join(save_dir, filename)
                if not os.path.isdir(save_path):
                    os.makedirs(save_path)

                # get num of valid filaments
                # this try/except section is kind of a safty check
                # only working files ie: files with data to parse should have actors created.
                try:
                    valid_filament_ids = get_valid_filaments(data_path=file_path)
                    run_summary[data_path][filename][
                        "all_filament_object_tracks"
                    ] = valid_filament_ids

                except NoFilamentsException:
                    print(
                        f"[info] -- file {filename} contains no filaments .. skipping"
                    )
                    run_summary[data_path][filename] = "No Filaments"
                    continue

                # if filament_ids are provided, filter valid_filament_ids
                if filament_ids:
                    valid_filament_ids = list(
                        filter(lambda x: (x + 1) in filament_ids, valid_filament_ids)
                    )

                # if finally no items are avialble display to user.
                if len(valid_filament_ids) == 0:
                    print(
                        f"[info] -- no valid filaments in {filename} .. skipping file"
                    )

                else:
                    print(
                        f"[info] -- creating {len(valid_filament_ids)} actors for {filename}"
                    )

                    # create actors for each filament in current imaris file
                    run_summary[data_path][filename]["extracted_filaments"] = []
                    for idx in valid_filament_ids:
                        actor = FilamentParserDistributed.remote(
                            file_path,
                            filament_id=idx,
                            save_dir=save_path,
                        )
                        actors.append(actor)

                        # update summary
                        run_summary[data_path][filename]["extracted_filaments"].append(
                            idx
                        )
                    print("\n")

            run_summary[data_path]["total filaments"] = len(actors)

        # generate results
        print(f"[info] -- found {len(actors)} actors")
        print(f"[info] -- extracting data ... ")

        run_ray_actors(actors, cpu_cores)

        print(f"[info] -- complete.")
