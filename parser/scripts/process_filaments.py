from typing import List, Tuple
from utils.utils import get_valid_filaments
from parsers.filament_parser import FilamentParserDistributed
from .processor import Processor


###############################################################################################
###############################################################################################
def run_filament_parser_parallel(
    data_dirs: List[str],
    save_dirs: List[str],
    cpu_cores: int = None,
    filament_ids: Tuple[int] = None,
    **kwargs,
) -> None:
    process = Processor(
        data_dirs=data_dirs,
        save_dirs=save_dirs,
        validator_fn=get_valid_filaments,
        parser_class=FilamentParserDistributed,
        parser_type="Filament",
        cpu_cores=cpu_cores,
        object_ids=filament_ids,
    )
    kwargs["logfile_name"] = "filament_parser"
    process.run(**kwargs)


###############################################################################################
###############################################################################################
