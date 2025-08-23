# put all I/O utils functions here
import os
import yaml
from typing import Dict


############################################################################
############################################################################
# function for loading yaml
def load_yaml(config_yaml_path: str) -> Dict:
    """_summary_

    Args:
        config_yaml_path (str): _description_

    Returns:
        Dict: _description_
    """
    assert os.path.isfile(config_yaml_path), "invalid config file path"
    with open(config_yaml_path) as f:
        data = yaml.safe_load(f)

    return data


############################################################################
############################################################################
