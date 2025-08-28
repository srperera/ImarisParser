import os
import sys
import glob
import numpy as np
from tqdm import tqdm
from pathlib import Path
from termcolor import colored
from typing import List, Tuple, Callable, Any, Type
from concurrent.futures import ProcessPoolExecutor, as_completed
from imaris.exceptions import *
from utils.logger import create_run_logfile, Logger


#############################################################################################
#############################################################################################
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

    def _create_logger(self, name: str = None) -> None:
        # Setup logger (redirect print)
        log_file = f"run.log"
        self.log_file = create_run_logfile(
            name, logfile_name=log_file, base_path=f"../run_logs/"
        )
        self._logger = Logger(self.log_file)
        # Logger(log_file)  # Redirect all prints to log and console
        sys.stdout = self._logger

    def _scan_and_collect_tasks(self, name) -> None:
        """
        Scan data directories, validate files, and prepare task list.

        Args: None

        Returns: None
        """
        print(f"\n[info] -- Starting {name.upper()}")
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
                    # always check if the item is valid
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

                except (NoPointsException, NoSurfaceException, NoFilamentsException):
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

    def _clean_up(self) -> None:
        # set stdout to its original instead of logger.
        sys.stdout.close()  # important!
        sys.stdout = sys.__stdout__
        sys.stdout.flush()
        sys.stdout = self._logger.terminal

    def run(self, **kwargs):
        """
        Orchestrates scanning, validating, and parallel execution.

        Args:
            validator_fn (Callable): Function for validating objects in the file.
            parser_class (Type): Parser class to process tasks.
        """
        self._create_logger(kwargs["logfile_name"])
        self._scan_and_collect_tasks(kwargs["logfile_name"])
        self._execute_in_parallel(**kwargs)
        self._clean_up()


#############################################################################################
#############################################################################################
