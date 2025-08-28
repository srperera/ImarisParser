import gc
import os
import pandas as pd
from typing import Dict
from copy import deepcopy
from .parser_base import Parser
from imaris.imaris import ImarisDataObject
from imaris.exceptions import NoSurfaceException

# Notes:
"""
* if init surface_id = -1 it will load all surfaces into memory
    * we can use a int surface_id value in extract or inspect to access info
    
* if init surface_id is given a specific value, it will only load that one surface info to memory
    * we have to use int surface_id = 0 in extract or inspect to access the corressponding data
    
* above two steps are done to help improve memory allocation during parallel execution.
"""


#############################################################################
class TimeStepSurfaceParserDistributed(Parser):
    """
    Extracts Surface Track Level Information From Imaris File.

    Args:
        Parser (ABCMeta): Parser Abstract Base Class
    """

    def __init__(
        self,
        ims_file_path: str,
        surface_id: int = -1,
        save_dir: str = None,
        time_step: float = 1.0,
    ) -> None:
        # TODO set up such that we can pass in a path of stats the user wants and we filter final csv accordingly
        self.ims_file_path = ims_file_path
        self.surface_id = surface_id
        self.save_dir = save_dir
        self.time_step = time_step
        self.ims = ImarisDataObject(self.ims_file_path)
        self._configure_instance(surface_id=surface_id)

        del self.ims
        gc.collect()

        # new addition
        self.filename = os.path.basename(ims_file_path).split(".")[0]

    def _configure_instance(self, surface_id: int) -> None:
        """
        Extracts relevant information from ims object and
        instantiates it as instance variables for fast recall.

        Currently Extracts:
            - all the surface names -- List
            - all the stats_names -- {id: pd.DataFrame}
            - all the stats values -- {id: pd.DataFrame}
            - all the factor info -- {id: pd.DataFrame}
        """
        # TODO: check to ensure surfaces exist or raise error
        # extract all information and saves it as a instance var
        if surface_id == -1:  # configure all available surfaces
            self.surface_names = self.ims.get_object_names("Surface")
        else:
            # grab the surface we care about
            self.surface_names = self.ims.get_object_names("Surface")
            if (surface_id >= 0) and (surface_id < len(self.surface_names)):
                self.surface_names = [self.surface_names[surface_id]]
                if self.surface_names[0] is None:
                    raise NoSurfaceException
            elif surface_id >= len(self.surface_names):
                raise ValueError(
                    f"surface_id {surface_id} exceeds number of surfaces available"
                )
            else:
                # some currently unknown error
                raise NotImplementedError("currently unknown errror lol")

        # get all the stats names for every surface {surf_id: stats_name_df}
        self.stats_names = {
            surface_id: self.ims.get_stats_names(surface_name)
            for surface_id, surface_name in enumerate(self.surface_names)
            if surface_name is not None
        }

        # get all the stats values for every surface {surf_id: stats_values_df}
        self.stats_values = {
            surface_id: self.ims.get_stats_values(surface_name)
            for surface_id, surface_name in enumerate(self.surface_names)
            if surface_name is not None
        }

        # get all the factor table info for every surface {surf_id: factor_df}
        self.factors = {
            surface_id: self.ims.get_object_factor(surface_name)
            for surface_id, surface_name in enumerate(self.surface_names)
            if surface_name is not None
        }

        # get all the factor table info for every surface {surf_id: factor_df}
        self.object_ids = {
            surface_id: self.ims.get_object_ids(surface_name)
            for surface_id, surface_name in enumerate(self.surface_names)
            if surface_name is not None
        }

    def _save_csv(
        self,
        dataframe: pd.DataFrame,
        save_dir: str,
        surface_id: int,
    ) -> None:
        # a function to write csv information to disk
        # get save_dir/original_filename.csv
        ims_filename = os.path.basename(self.ims_file_path).split(".")[0]
        ims_filename = (
            f"{ims_filename}_surface_{(surface_id + 1)}_timestep_{self.time_step}.csv"
        )
        save_filepath = os.path.join(save_dir, ims_filename)
        dataframe.to_csv(save_filepath)

        # store ims_filename
        self.ims_filename = ims_filename

    def _process(self, surface_id: int) -> None:
        """
        Runs a single end to end parser pipeline on a single surface
        Steps:
            - get stat names for a single surface
            - get stat values for a single surface
            - filter stat values to keep only track ids
            - filter stats values to remove track level stat information
            - rename certian columns (if needed)(need a custom func for this to add channel info)
            - organize the filtered stats
            - generate csv
            - save csv

        Args:
            surface_id (int): _description_
        """
        if (self.surface_id != -1) and (surface_id != 0):
            raise ValueError(
                f"class is initialized with 1 surface, surface_id should be set to 0"
            )

        # check 2
        if surface_id > len(self.surface_names):
            raise ValueError(
                f"surface_id {surface_id} exceeds number of surfaces available {len(self.surface_names)}"
            )

        # gather info for current surface
        surface_name = self.surface_names[surface_id]
        stat_names = self.stats_names.get(surface_id)
        stat_values = self.stats_values.get(surface_id)
        object_id = self.object_ids.get(surface_id)
        factor = self.factors.get(surface_id)

        # update channel and surface names
        stat_names = self._update_channel_info_fast(stat_names, factor)

        # update surface names
        stat_names = self._update_surface_info_fast(stat_names, factor)

        # filter stats values by object ids and time index = time_step
        # here we are just trying to find the object ids that at time_step
        time_index_id = stat_names[stat_names["Name"] == "Time Index"]["ID"]
        time_index_id = time_index_id.iloc[0].item()
        object_ids_at_timestep = self._filter_stats(
            stats_values=deepcopy(stat_values),
            filter_col_names=["ID_Object", "ID_StatisticsType", "Value"],
            filter_values=[
                object_id,
                pd.Series([time_index_id]),
                pd.Series([self.time_step]),
            ],
        )["ID_Object"]

        # filter stats values by object ids (ie: ignore info related to trackids)
        stat_values = self._filter_stats(
            stats_values=stat_values,
            filter_col_names=["ID_Object"],
            filter_values=[object_ids_at_timestep],
        )

        # organize stats value
        organized_stats = self._organize_stats_fast(stat_values)

        # generate csv
        stats_df = self._format_data(organized_stats, stat_names=stat_names)

        return stats_df

    def extract_and_save(self, idx: int, save_dir: str = None) -> None:
        # this function is the funtion that gets called externally
        # we can have this function as a ray method to help with distributed execution
        # check 1

        # process surface
        dataframe = self._process(idx)

        # adjust surface_id based on init mode
        # save surface
        save_dir = save_dir if save_dir else self.save_dir
        if self.surface_id == -1:
            self._save_csv(dataframe, save_dir, surface_id=idx)
        else:
            self._save_csv(dataframe, save_dir, surface_id=self.surface_id)

        # print(f"[info] -- finished: {self.ims_filename}")

    def inspect(self, surface_id: int) -> Dict:
        """
        Runs a single end to end parser pipeline on a single surface
        and returns all components as a dict.
        Steps:
            - get stat names for a single surface
            - get stat values for a single surface
            - filter stat values to keep only track ids
            - filter stats values to remove track level stat information
            - rename certian columns (if needed)(need a custom func for this to add channel info)
            - organize the filtered stats
            - generate csv
            - save csv

        Args:
            surface_id (int): _description_
        """
        # check 1
        if (self.surface_id != -1) and (surface_id != 0):
            raise ValueError(
                f"class is initialized with 1 surface, surface_id should be set to 0"
            )

        # check 2
        if surface_id > len(self.surface_names):
            raise ValueError(
                f"surface_id {surface_id} exceeds number of surfaces available {len(self.surface_names)}"
            )

        # dict to hold all values to be returned for inspection
        storage = {}

        # gather info for current surface
        surface_name = self.surface_names[surface_id]
        storage["surface_name"] = surface_name
        stat_names = self.stats_names.get(surface_id)
        storage["stat_names_raw"] = stat_names
        stat_values = self.stats_values.get(surface_id)
        storage["stat_values_raw"] = stat_values
        object_id = self.object_ids.get(surface_id)
        storage["object_id"] = object_id
        factor = self.factors.get(surface_id)
        storage["factor"] = factor

        # update channel and surface names
        stat_names = self._update_channel_info_fast(
            stats_names=deepcopy(stat_names),
            factor=factor,
        )
        storage["stat_names_channel_info_fast"] = deepcopy(stat_names)

        # update surface names
        stat_names = self._update_surface_info_fast(
            stats_names=deepcopy(stat_names),
            factor=factor,
        )
        storage["stat_names_surface_info_fast"] = deepcopy(stat_names)

        # filter stats values by object ids and time index = time_step
        # here we are just trying to find the object ids that at time_step
        time_index_id = stat_names[stat_names["Name"] == "Time Index"]["ID"]
        time_index_id = time_index_id.iloc[0].item()
        object_ids_at_timestep = self._filter_stats(
            stats_values=deepcopy(stat_values),
            filter_col_names=["ID_Object", "ID_StatisticsType", "Value"],
            filter_values=[
                object_id,
                pd.Series([time_index_id]),
                pd.Series([self.time_step]),
            ],
        )["ID_Object"]
        storage["object_ids_at_timestep"] = object_ids_at_timestep

        # filter stats values by object ids (ie: ignore info related to trackids)
        stat_values = self._filter_stats(
            stats_values=stat_values,
            filter_col_names=["ID_Object"],
            filter_values=[object_ids_at_timestep],
        )
        storage["stat_values_filtered"] = stat_values

        # create dict that maps stat id to name
        stats_dict = dict(zip(stat_names["ID"], stat_names["Name"]))
        storage["stats_dict"] = stats_dict

        # keep only unique for display
        available_stats_names = [
            stats_dict[ids] for ids in stat_values["ID_StatisticsType"].unique()
        ]
        storage["available_stats_names"] = available_stats_names

        # organize stats value (most compute used here)
        organized_stats = self._organize_stats_fast(stat_values)
        storage["organized_stats_fast"] = organized_stats

        # generate csv
        stats_df = self._format_data(organized_stats, stat_names=stat_names)
        storage["final_df"] = stats_df

        # TODO: do we need to inject in track information here??
        # do objects that dont belong to a track have first time points?

        # add track id information for each object
        #
        # stats_df = self._update_track_id_info(surface_id, stats_df)
        # print(f"get _update_track_id_info time: {time.perf_counter() - start}")
        # storage["final_df"] = stats_df

        # stats_df2 = self._update_track_id_info(surface_id, stats_df2)
        # storage["final_df2"] = stats_df2

        return storage


#############################################################################
