from typing import List, Tuple
from parsers.surface_parser import SurfaceParserDistributed
from parsers.surface_track_parser import SurfaceTrackParserDistributed
from utils.utils import get_valid_surfaces, get_valid_surfaces_with_tracks
from parsers.surface_time_step_parser import TimeStepSurfaceParserDistributed
from parsers.surface_track_object_parser import SurfaceTrackObjectParserDistributed
from .processor import Processor


###############################################################################################
###############################################################################################
def run_surface_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    surface_ids: Tuple[int] = None,
    **kwargs,
) -> None:

    process = Processor(
        data_dirs=data_dirs,
        save_dirs=save_dirs,
        validator_fn=get_valid_surfaces,
        parser_class=SurfaceParserDistributed,
        parser_type="Surface",
        cpu_cores=cpu_cores,
        object_ids=surface_ids,
    )
    kwargs["logfile_name"] = "surface"
    process.run(**kwargs)


###############################################################################################
###############################################################################################
def run_surface_track_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    surface_ids: Tuple[int] = None,
    **kwargs,
) -> None:

    process = Processor(
        data_dirs=data_dirs,
        save_dirs=save_dirs,
        validator_fn=get_valid_surfaces_with_tracks,
        parser_class=SurfaceTrackParserDistributed,
        parser_type="Surface",
        cpu_cores=cpu_cores,
        object_ids=surface_ids,
    )
    kwargs["logfile_name"] = "surface_track"
    process.run(**kwargs)


###############################################################################################
###############################################################################################
def run_surface_track_object_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    surface_ids: Tuple[int] = None,
    **kwargs,
) -> None:

    process = Processor(
        data_dirs=data_dirs,
        save_dirs=save_dirs,
        validator_fn=get_valid_surfaces,
        parser_class=SurfaceTrackObjectParserDistributed,
        parser_type="Surface",
        cpu_cores=cpu_cores,
        object_ids=surface_ids,
    )
    kwargs["logfile_name"] = "surface_track_object"
    process.run(**kwargs)


###############################################################################################
###############################################################################################
def run_surface_timestep_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    surface_ids: Tuple[int] = None,
    **kwargs,
) -> None:

    process = Processor(
        data_dirs=data_dirs,
        save_dirs=save_dirs,
        validator_fn=get_valid_surfaces,
        parser_class=TimeStepSurfaceParserDistributed,
        parser_type="Surface",
        cpu_cores=cpu_cores,
        object_ids=surface_ids,
    )
    kwargs["logfile_name"] = "surface_timestep"
    process.run(**kwargs)
