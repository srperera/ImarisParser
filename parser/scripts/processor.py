import os
import glob
import numpy as np
from tqdm import tqdm
from pathlib import Path
from termcolor import colored
from typing import List, Tuple, Callable, Any, Type
from concurrent.futures import ProcessPoolExecutor, as_completed
from imaris.exceptions import NoPointsException, NoDataException


class Processor:
    """
    Handles parallel execution of the parsers.
    Ideally we want this parser to be extendable to any parser.
    Because the logic is basically the same across all parsers

    Attributes:
        data_dirs (List[str]): List of directories containing Imaris files.
        save_dirs (List[str]): List of directories to save parsed data.
        cpu_cores (int): Number of CPU cores to use. Defaults to all available.
        spot_ids (Tuple[int]): Optional tuple of specific spot IDs to parse.
    """

    def __init__(
        self,
        data_dirs: List[str],
        save_dirs: List[str],
        validator_fn: Callable,
        parser_class: Type[Any],
        parser_type: str = "Surface",
        cpu_cores: int = None,
        object_ids: Tuple[int] = None,
    ):
        if object_ids and not isinstance(object_ids, tuple):
            raise TypeError("object_ids must be a tuple")

        self.data_dirs = data_dirs
        self.save_dirs = save_dirs
        self.cpu_cores = cpu_cores
        self.object_ids = object_ids
        self.tasks = []
        self.run_summary = {}

        # parser specific items
        self.validator_fn = validator_fn
        self.parser_class = parser_class
        self.parser_type = parser_type

    def _scan_and_collect_tasks(self) -> None:
        """
        Scan data directories, validate files, and prepare task list.

        Args: None

        Returns: None
        """
        for data_path, save_dir in zip(self.data_dirs, self.save_dirs):
            print(f"[info] -- Scanning folder: {data_path}")
            imaris_files = glob.glob(os.path.join(os.path.abspath(data_path), "*.ims"))
            self.run_summary[data_path] = {}

            if not imaris_files:
                print(f"[info] -- Skipping folder, no .ims files found.")
                self.run_summary[data_path] = None
                continue

            for file_path in imaris_files:
                print(f"[info] -- Filename: {colored(f'"{file_path}"', 'red')}")
                filename = os.path.splitext(os.path.basename(file_path))[0]
                save_path = os.path.join(save_dir, filename)
                os.makedirs(save_path, exist_ok=True)

                try:
                    valid_objects = self.validator_fn(file_path)

                    if self.object_ids:
                        valid_objects = [
                            idx for idx in valid_objects if (idx + 1) in self.object_ids
                        ]

                    if valid_objects:
                        print(
                            f"\t[info] -- Found {colored(valid_objects, 'green')} {self.parser_type}s in File Name: {colored(filename, 'green')}"
                        )
                        for idx in valid_objects:
                            self.tasks.append((Path(file_path), idx, save_path))
                    else:
                        print(
                            f"\t[info] -- No valid {self.parser_type}s found in File: {colored(filename, 'red')} after filtering."
                        )

                except NoPointsException:
                    print(
                        f"\t[info] -- File: {colored(f'\"{file_path}\"', 'red')} contains no {self.parser_type}s. Skipping."
                    )
                except NoDataException:
                    print(
                        f"\t[info] -- File: {colored(f'\"{file_path}\"', 'red')} contains no data. Skipping."
                    )
                except Exception as e:
                    print(
                        f"\t[error] -- Filename: {colored(f'\"{file_path}\"', 'red')} generated an unhandled exception: {colored(e, 'yellow')} . Skipping."
                    )

    def _execute_in_parallel(self, **kwargs) -> None:
        """
        Execute prepared tasks in parallel using ProcessPoolExecutor.

        Args: None

        Returns: None
        """
        if not self.tasks:
            print("\n[info] -- No tasks to run. Exiting.")
            return

        print(f"\n[info] -- Found a total of {len(self.tasks)} tasks.")
        print(f"[info] -- Starting parallel extraction...")

        with ProcessPoolExecutor(max_workers=self.cpu_cores) as executor:
            # TODO: We can move the actor creation and splits logic outside the with statement.
            actors = []
            for task in tqdm(
                self.tasks,
                total=len(self.tasks),
                colour="Yellow",
                ncols=80,
                desc="Configuring Parser",
            ):
                try:
                    actor = self.parser_class(*task, **kwargs)
                    actors.append(actor)
                except Exception as e:
                    print(
                        f"\t[error] -- File {colored(f'"{task[0]}"', 'red')} generated an exception: {colored(e, 'yellow')}"
                    )
                    continue

            # ensure we are not submitting too many jobs at a time
            # limits to at most 1 task per core.
            num_actors = len(actors)
            num_splits = (
                int(np.round(num_actors / self.cpu_cores))
                if num_actors > self.cpu_cores
                else 1
            )
            splits = np.array_split(np.asarray(actors, dtype=object), num_splits)

            # Process
            for idx, split in enumerate(splits):
                future_to_task = [
                    executor.submit(actor.extract_and_save, *[0]) for actor in split
                ]

                for future in tqdm(
                    as_completed(future_to_task),
                    total=len(split),
                    colour="MAGENTA",
                    ncols=80,
                    desc=f"Processing split {idx}",
                ):
                    try:
                        future.result()
                    except Exception as e:
                        print(
                            f"\t[error] -- File {colored(f'"{task[0]}"', 'red')} with {self.parser_type} ID {colored(task[1], 'red')} generated an exception: {colored(e, 'yellow')}"
                        )
                        continue

        print("\n[info] -- All tasks complete.")

    def run(self, **kwargs):
        """
        Orchestrates scanning, validating, and parallel execution.

        Args:
            validator_fn (Callable): Function for validating objects in the file.
            parser_class (Type): Parser class to process tasks.
        """
        self._scan_and_collect_tasks()
        self._execute_in_parallel(**kwargs)
