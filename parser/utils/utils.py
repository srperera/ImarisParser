import gc
import ray
import numpy as np
from typing import List
from imaris.imaris import ImarisDataObject

# from parsers.surface_parser import SurfaceParserDistributed
from imaris.exceptions import *


#########################################################################################
def get_num_surfaces(data_path: str) -> int:
    """
    Returns number of surfaces in given Imaris File
    Args:
        data_path (str): _description_
        valid (bool, optional): _description_. Defaults to True.

    Returns:
        int: _description_
    """
    ims_obj = ImarisDataObject(data_path)
    num_surfaces = len(ims_obj.get_object_names("Surface"))
    return num_surfaces


#########################################################################################
def surface_contains_tracks(data_path: str, surface_id: int = 0) -> bool:
    """Checks ims file to see if track information is avilable for a given surface.

    Args:
        data_path (str): path to ims file
        surface_id (int, optional): surface id value. Defaults to 0.

    Returns:
        bool: Returns True if track information is avilable else False
    """
    ims_obj = ImarisDataObject(data_path)
    surface_names = ims_obj.get_object_names("Surface")
    return ims_obj.contains_tracks(surface_names[surface_id])


#########################################################################################
def contains_sufaces(data_path: str, surface_id: int = 0) -> bool:
    """Checks ims file to see if surface information is avilable.

    Args:
        data_path (str): path to ims file
        surface_id (int, optional): surface id value. Defaults to 0.

    Returns:
        bool: Returns True if track information is avilable else False
    """
    ims_obj = ImarisDataObject(data_path)
    surface_names = ims_obj.get_object_names("Surface")
    return ims_obj.contains_sufaces(surface_names[surface_id])


#########################################################################################
def get_surface_stats(data_path: str, surface_id: int = -1) -> List[str]:
    """
    INCOMPLETE

    Args:
        data_path (str): _description_
        surface_id (int, optional): _description_. Defaults to -1.

    Raises:
        ValueError: _description_

    Returns:
        List[str]: _description_
    """
    num_surfaces = get_num_surfaces(data_path)  # num available surfaces
    parser = SurfaceParser(data_path)
    # grab all
    if surface_id == -1:  # grab all
        available_stats_storage = [
            parser.get_surface_info(surface_id=idx) for idx in range(num_surfaces)
        ]
        return available_stats_storage

    elif surface_id <= num_surfaces:
        available_stats_storage = parser.get_surface_info(surface_id)
        return available_stats_storage

    else:
        raise ValueError("requested surface id exceeeds number of surfaces available")


#########################################################################################
def get_valid_surfaces(data_path: str) -> List[int]:
    """
    Returns a list of surfaces that contains surface stats
    because some surfaces might not contain statistics.

    Args:
        data_path (str): path to imaris file.

    Returns:
        List: _description_
    """
    ims_obj = ImarisDataObject(data_path)
    surface_names = ims_obj.get_object_names("Surface")
    valid_surfaces = []
    for idx, surface in enumerate(surface_names):
        valid_surface = ims_obj.contains_surfaces(surface)
        if valid_surface:
            valid_surfaces.append(idx)
        print(f"[info] -- surface id: {idx} -- surface: {valid_surface}")

    return valid_surfaces


#########################################################################################
def get_valid_filaments(data_path: str) -> List[int]:
    """
    Returns a list of filaments that contains filament stats
    because some filament might not contain statistics.

    Args:
        data_path (str): path to imaris file.

    Returns:
        List: _description_
    """
    ims_obj = ImarisDataObject(data_path)
    filement_names = ims_obj.get_object_names("Filament")
    valid_filaments = []
    for idx, filement in enumerate(filement_names):
        valid_filement = ims_obj.contains_filaments(filement)
        if valid_filement:
            valid_filaments.append(idx)
        print(f"[info] -- filament id: {idx} -- filament: {valid_filement}")

    return valid_filaments


#########################################################################################
def get_valid_track_surfaces(data_path: str) -> List[int]:
    """
    Returns a list of surfaces that contains surface stats and
    track information because some surfaces might not contain tracks.

    Args:
        data_path (str): path to imaris file.

    Returns:
        List: _description_
    """
    ims_obj = ImarisDataObject(data_path)
    surface_names = ims_obj.get_object_names("Surface")
    valid_surfaces = []
    for idx, surface in enumerate(surface_names):
        valid_surface = ims_obj.contains_surfaces(surface)
        valid_track = ims_obj.contains_tracks(surface)
        if valid_surface and valid_track:
            valid_surfaces.append(idx)

        print(
            f"[info] -- surface id: {idx} -- surface: {valid_surface} -- tracks: {valid_track}"
        )

    return valid_surfaces


#########################################################################################
def run_ray_actors(actors: List, cpu_cores: int):
    # generate results
    # split if too many actors vs cores else run all
    if cpu_cores and cpu_cores < len(actors):
        num_actors = len(actors)
        num_splits = np.round(num_actors / cpu_cores)
        splits = np.array_split(np.asarray(actors, dtype=object), num_splits)
        for split in splits:
            # .remote(0) because we init each actor with one item. so 0 grabs that one item.
            tasks = [
                actor.extract_and_save.remote(idx=0) for _, actor in enumerate(split)
            ]
            ready_tasks, _ = ray.wait(tasks, num_returns=len(tasks))
            results = ray.get(ready_tasks)
    else:
        tasks = [actor.extract_and_save.remote(idx=0) for _, actor in enumerate(actors)]
        ready_tasks, _ = ray.wait(tasks, num_returns=len(tasks))
        results = ray.get(ready_tasks)


#########################################################################################
# TODO: Combine the run_ray_actors
# TODO: Need to unify surface_id / filament_ids so we dont have to change keywords
def run_ray_filament_actors(actors: List, cpu_cores: int):
    # generate results
    # split if too many actors vs cores else run all
    if cpu_cores and cpu_cores < len(actors):
        num_actors = len(actors)
        num_splits = np.round(num_actors / cpu_cores)
        splits = np.array_split(np.asarray(actors, dtype=object), num_splits)
        for split in splits:
            tasks = [
                actor.extract_and_save.remote(filament_id=0)
                for _, actor in enumerate(split)
            ]
            ready_tasks, _ = ray.wait(tasks, num_returns=len(tasks))
            results = ray.get(ready_tasks)
    else:
        tasks = [
            actor.extract_and_save.remote(filament_id=0)
            for _, actor in enumerate(actors)
        ]
        ready_tasks, _ = ray.wait(tasks, num_returns=len(tasks))
        results = ray.get(ready_tasks)


#########################################################################################
def run_ray_actors_2(actors: List, cpu_cores: int):
    # generate results
    # split if too many actors vs cores else run all
    if cpu_cores and cpu_cores < len(actors):
        num_actors = len(actors)
        num_splits = np.round(num_actors / cpu_cores)
        splits = np.array_split(np.asarray(actors, dtype=object), num_splits)
        for split in splits:
            for actor in split:
                actor.extract_and_save(surface_id=0)
    else:
        for actor in split:
            actor.extract_and_save(surface_id=0)


#########################################################################################
#########################################################################################
def get_valid_spot_objects(data_path: str) -> List[int]:
    """
    Returns a list of points that contains points/spot stats
    because some points might not contain statistics.

    Args:
        data_path (str): path to imaris file.

    Returns:
        List: _description_

    *** WORKING V2
    """
    ims_obj = ImarisDataObject(data_path)
    points_names = ims_obj.get_object_names("Points")
    valid_points = []
    for idx, point in enumerate(points_names):
        valid_point = ims_obj.contains_points(point)
        if valid_point:
            valid_points.append(idx)
            print(f"[info] -- points id: {idx} -- points: {point} -- Valid")
        else:
            print(f"[info] -- points id: {idx} -- points: {point} -- Invalid Skipping")

    return valid_points


#########################################################################################
#########################################################################################
def get_valid_spot_tracks(data_path: str) -> List[int]:
    """
    Returns a list of points that contains points/spot stats
    because some points might not contain statistics.

    Args:
        data_path (str): path to imaris file.

    Returns:
        List: _description_

    *** WORKING V2
    """
    ims_obj = ImarisDataObject(data_path)
    points_names = ims_obj.get_object_names("Points")
    valid_points = []
    for idx, point in enumerate(points_names):
        valid_point = ims_obj.contains_tracks(point)
        if valid_point:
            valid_points.append(idx)
            print(f"[info] -- points id: {idx} -- points: {point} -- Valid")
        else:
            print(f"[info] -- points id: {idx} -- points: {point} -- Invalid Skipping")

    return valid_points


#########################################################################################
#########################################################################################
def get_valid_filaments(data_path: str) -> List[int]:
    """
    Returns a list of filaments that contains filament stats
    because some filament might not contain statistics.

    Args:
        data_path (str): path to imaris file.

    Returns:
        List: _description_

    *** WORKING V2
    """
    ims_obj = ImarisDataObject(data_path)
    filament_names = ims_obj.get_object_names("Filaments")
    valid_filaments = []
    for idx, filament in enumerate(filament_names):
        valid_filament = ims_obj.contains_filaments(filament)
        if valid_filament:
            valid_filaments.append(idx)
            print(f"[info] -- filament id: {idx} -- filament: {filament} -- Valid")
        else:
            print(
                f"[info] -- filament id: {idx} -- filament: {filament} -- Invalid Skipping"
            )

    return valid_filaments


#########################################################################################
#########################################################################################
def run_ray_actors(actors: List, cpu_cores: int):
    """V2 Working"""
    # generate results
    # split if too many actors vs cores else run all
    if cpu_cores and cpu_cores < len(actors):
        num_actors = len(actors)
        num_splits = np.round(num_actors / cpu_cores)
        splits = np.array_split(np.asarray(actors, dtype=object), num_splits)
        for split in splits:
            # .remote(0) because we init each actor with one item. so 0 grabs that one item.
            tasks = [
                actor.extract_and_save.remote(idx=0) for _, actor in enumerate(split)
            ]
            ready_tasks, _ = ray.wait(tasks, num_returns=len(tasks))
            results = ray.get(ready_tasks)
    else:
        tasks = [actor.extract_and_save.remote(idx=0) for _, actor in enumerate(actors)]
        ready_tasks, _ = ray.wait(tasks, num_returns=len(tasks))
        results = ray.get(ready_tasks)


#########################################################################################
#########################################################################################
def get_valid_surfaces(data_path: str) -> List[int]:
    """
    Returns a list of surfaces that contains surface stats
    because some surfaces might not contain statistics.

    Args:
        data_path (str): path to imaris file.

    Returns:
        List: _description_

    ** WORKING V2
    """
    ims_obj = ImarisDataObject(data_path)
    surface_names = ims_obj.get_object_names("Surface")
    valid_surfaces = []
    for idx, surface in enumerate(surface_names):
        valid_surface = ims_obj.contains_surfaces(surface)
        if valid_surface:
            valid_surfaces.append(idx)
            print(f"[info] -- surface id: {idx} -- surface: {surface} -- Valid")
        else:
            print(
                f"[info] -- surface id: {idx} -- surface: {surface} -- Invalid Skipping"
            )

    return valid_surfaces


#########################################################################################
#########################################################################################
def get_valid_surfaces_with_tracks(data_path: str) -> List[int]:
    """
    Returns a list of surfaces that contains surface stats and
    track information because some surfaces might not contain tracks.

    Here we are only concerned about checking if surfaces have track information.
    Because we want to extract only the track statistics.

    Args:
        data_path (str): path to imaris file.

    Returns:
        List: _description_
    """
    ims_obj = ImarisDataObject(data_path)
    surface_names = ims_obj.get_object_names("Surface")
    valid_surfaces = []
    for idx, surface in enumerate(surface_names):
        valid_surface = ims_obj.contains_surfaces(surface)
        valid_track = ims_obj.contains_tracks(surface)
        if valid_surface and valid_track:
            valid_surfaces.append(idx)
            print(
                f"[info] -- surface id: {idx} -- surface: {surface} -- Valid w/ Tracks"
            )
        else:
            print(
                f"[info] -- surface id: {idx} -- surface: {surface} -- Invalid no Tracks .. Skipping"
            )

    return valid_surfaces
