from typing import List
from imaris.exceptions import *
from imaris.imaris import ImarisDataObject


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
        if point is None:
            valid_point = False
        else:
            valid_point = ims_obj.contains_points(point)
        if valid_point:
            valid_points.append(idx)
            print(f"\t[info] -- points id: {idx} -- points: {point} -- Valid")
        else:
            print(
                f"\t[info] -- points id: {idx} -- points: {point} -- Invalid Skipping"
            )

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
        if point is None:
            valid_point = False
        else:
            valid_point = ims_obj.contains_tracks(point)
        if valid_point:
            valid_points.append(idx)
            print(f"\t[info] -- points id: {idx} -- points: {point} -- Valid")
        else:
            print(
                f"\t[info] -- points id: {idx} -- points: {point} -- Invalid (No Tracks)"
            )

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
        if filament is None:
            valid_filament = False
        else:
            valid_filament = ims_obj.contains_filaments(filament)
        if valid_filament:
            valid_filaments.append(idx)
            print(f"\t[info] -- filament id: {idx} -- filament: {filament} -- Valid")
        else:
            print(
                f"\t[info] -- filament id: {idx} -- filament: {filament} -- Invalid Skipping"
            )

    return valid_filaments


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
        if surface is None:
            valid_surface = False
        else:
            valid_surface = ims_obj.contains_surfaces(surface)
        if valid_surface:
            valid_surfaces.append(idx)
            print(f"\t[info] -- surface id: {idx} -- surface: {surface} -- Valid")
        else:
            print(
                f"\t[info] -- surface id: {idx} -- surface: {surface} -- Invalid Skipping"
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

    *** WORKING V2
    """
    ims_obj = ImarisDataObject(data_path)
    surface_names = ims_obj.get_object_names("Surface")
    valid_surfaces = []
    for idx, surface in enumerate(surface_names):
        if surface is None:
            valid_surface = False
            valid_track = False
        else:
            valid_surface = ims_obj.contains_surfaces(surface)
            valid_track = ims_obj.contains_tracks(surface)
        if valid_surface and valid_track:
            valid_surfaces.append(idx)
            print(
                f"\t[info] -- surface id: {idx} -- surface: {surface} -- Valid w/ Tracks"
            )
        else:
            print(
                f"\t[info] -- surface id: {idx} -- surface: {surface} -- Invalid no Tracks .. Skipping"
            )

    return valid_surfaces


#########################################################################################
#########################################################################################
