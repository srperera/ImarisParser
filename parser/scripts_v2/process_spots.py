import os
import glob
from typing import List, Tuple
from imaris.exceptions import NoPointsException
from parsers_v2.spot_track_parser import SpotTrackParserDistributed
from parsers_v2.spot_track_object_parser import SpotTrackObjectParserDistributed
from utils.utils import get_valid_spot_objects, run_ray_actors, get_valid_spot_tracks

"""
Notes:
    available functions:
        * run_spot_parser_parallel
        * run_spot_parser_parallel_index

    We should do all the necessary checks before creating actors
        *ie: check for valid spots, tracks etc
        * makes everything cleaner
"""


###############################################################################################
###############################################################################################
def run_spot_track_object_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    spot_ids: Tuple[int] = None,
) -> None:
    """
    Runs ALL spots in an ims file in parallel.
    Pipeline:
        - For every file in every directory
        - Create a folder a with the same name as the filename inside save_dir provided
        - For every spot inside each file we create a remote actor
        - Once all actors are created we can use the cpu cores provided by user to
            run a fixed chunk of actors in parallel so we dont start too many instances at one
        - If no cpu_cores provided we will run all actors in parallel

    Args:
        data_dirs (List[str]): _description_
        save_dirs (List[str]): _description_
        cpu_cores (int, optional): _description_. Defaults to None.
        spot_ids (Tuple[int], optional): _description_. Defaults to None.
    """
    if spot_ids:
        assert isinstance(spot_ids, tuple), "spot_ids must be a tuple"
        assert len(spot_ids) > 0, "spot_ids must not be empty"

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
        # we must only load the ones we want for Spots.
        else:
            for file_path in imaris_files:

                # get filename from path
                filename = os.path.splitext(os.path.basename(file_path))[0]
                run_summary[data_path][filename] = {}

                # create dir with same name as filename
                save_path = os.path.join(save_dir, filename)
                if not os.path.isdir(save_path):
                    os.makedirs(save_path)

                # get num of valid spots
                # this try/except section is kind of a safty check
                # only working files ie: files with data to parse should have actors created.
                try:
                    valid_spot_ids = get_valid_spot_objects(data_path=file_path)
                    run_summary[data_path][filename][
                        "all_spot_object_tracks"
                    ] = valid_spot_ids

                except NoPointsException:
                    print(f"[info] -- file {filename} contains no spots .. skipping")
                    run_summary[data_path][filename] = "NO spot TRACKS"
                    continue

                # if spot_ids are provided, filter valid_spot_ids
                if spot_ids:
                    valid_spot_ids = list(
                        filter(lambda x: (x + 1) in spot_ids, valid_spot_ids)
                    )

                # if finally no items are avialble display to user.
                if len(valid_spot_ids) == 0:
                    print(f"[info] -- no valid spots in {filename} .. skipping file")

                else:
                    print(
                        f"[info] -- creating {len(valid_spot_ids)} actors for {filename}"
                    )

                    # create actors for each spot in current imaris file
                    run_summary[data_path][filename]["extracted_spot_tracks"] = []
                    for idx in valid_spot_ids:
                        actor = SpotTrackObjectParserDistributed.remote(
                            file_path,
                            spot_id=idx,
                            save_dir=save_path,
                        )
                        actors.append(actor)

                        # update summary
                        run_summary[data_path][filename][
                            "extracted_spot_tracks"
                        ].append(idx)
                    print("\n")

            run_summary[data_path]["total spot tracks"] = len(actors)

        # generate results
        print(f"[info] -- found {len(actors)} actors")
        print(f"[info] -- extracting data ... ")

        run_ray_actors(actors, cpu_cores)

        print(f"[info] -- complete.")


###############################################################################################
def run_spot_track_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    spot_ids: Tuple[int] = None,
) -> None:
    """
    Runs ALL spots in an ims file in parallel.
    Pipeline:
        - For every file in every directory
        - Create a folder a with the same name as the filename inside save_dir provided
        - For every spot inside each file we create a remote actor
        - Once all actors are created we can use the cpu cores provided by user to
            run a fixed chunk of actors in parallel so we dont start too many instances at one
        - If no cpu_cores provided we will run all actors in parallel

    Args:
        data_dirs (List[str]): _description_
        save_dirs (List[str]): _description_
        cpu_cores (int, optional): _description_. Defaults to None.
        spot_ids (Tuple[int], optional): _description_. Defaults to None.
    """
    if spot_ids:
        assert isinstance(spot_ids, tuple), "spot_ids must be a tuple"
        assert len(spot_ids) > 0, "spot_ids must not be empty"

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
        # we must only load the ones we want for Spots.
        else:
            for file_path in imaris_files:

                # get filename from path
                filename = os.path.splitext(os.path.basename(file_path))[0]
                run_summary[data_path][filename] = {}

                # create dir with same name as filename
                save_path = os.path.join(save_dir, filename)
                if not os.path.isdir(save_path):
                    os.makedirs(save_path)

                # get num of valid spots
                # this try/except section is kind of a safty check
                # only working files ie: files with data to parse should have actors created.
                try:
                    valid_spot_ids = get_valid_spot_tracks(data_path=file_path)
                    run_summary[data_path][filename]["all_spot_tracks"] = valid_spot_ids

                except NoPointsException:
                    print(
                        f"[info] -- file {filename} contains no spots tracks.. skipping"
                    )
                    run_summary[data_path][filename] = "No Spot TRACKS"
                    continue

                # if spot_ids are provided, filter valid_spot_ids
                if spot_ids:
                    valid_spot_ids = list(
                        filter(lambda x: (x + 1) in spot_ids, valid_spot_ids)
                    )

                # if finally no items are avialble display to user.
                if len(valid_spot_ids) == 0:
                    print(f"[info] -- no valid spots in {filename} .. skipping file")

                else:
                    print(
                        f"[info] -- creating {len(valid_spot_ids)} actors for {filename}"
                    )

                    # create actors for each spot in current imaris file
                    run_summary[data_path][filename]["extracted_spot_tracks"] = []
                    for idx in valid_spot_ids:
                        actor = SpotTrackParserDistributed.remote(
                            file_path,
                            spot_id=idx,
                            save_dir=save_path,
                        )
                        actors.append(actor)

                        # update summary
                        run_summary[data_path][filename][
                            "extracted_spot_tracks"
                        ].append(idx)
                    print("\n")

            run_summary[data_path]["total spot tracks"] = len(actors)

        # generate results
        print(f"[info] -- found {len(actors)} actors")
        print(f"[info] -- extracting data ... ")

        run_ray_actors(actors, cpu_cores)

        print(f"[info] -- complete.")
