from typing import List, Tuple
from parsers.spot_track_parser import SpotTrackParserDistributed
from utils.utils import get_valid_spot_objects, get_valid_spot_tracks
from parsers.spot_track_object_parser import SpotTrackObjectParserDistributed
from .processor import Processor


###############################################################################################
###############################################################################################
def run_spot_track_object_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    spot_ids: Tuple[int] = None,
    **kwargs,
) -> None:
    process = Processor(
        data_dirs=data_dirs,
        save_dirs=save_dirs,
        validator_fn=get_valid_spot_objects,
        parser_class=SpotTrackObjectParserDistributed,
        parser_type="Spot",
        cpu_cores=cpu_cores,
        object_ids=spot_ids,
    )
    process.run(**kwargs)


###############################################################################################
###############################################################################################
def run_spot_track_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    spot_ids: Tuple[int] = None,
    **kwargs,
) -> None:
    process = Processor(
        data_dirs=data_dirs,
        save_dirs=save_dirs,
        validator_fn=get_valid_spot_tracks,
        parser_class=SpotTrackParserDistributed,
        parser_type="Spot",
        cpu_cores=cpu_cores,
        object_ids=spot_ids,
    )
    process.run(**kwargs)


###############################################################################################
###############################################################################################
