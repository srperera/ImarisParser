import gc
import os
import time
import pandas as pd
from copy import deepcopy
from functools import partial
from typing import Dict, List
from .parser_base import Parser
from imaris.imaris import ImarisDataObject


###########################################################################################
###########################################################################################
# @ray.remote
class SurfaceTrackObjectParserDistributed(Parser):
    """
    Extracts Surface Level Information From Imaris File

    Args:
        Parser (ABCMeta): Parser Abstract Base Class
    """

    def __init__(
        self,
        ims_file_path: str,
        surface_id: int = -1,
        save_dir: str = None,
    ) -> None:
        """
        Args:
            * ims_file_path (str): path to .ims file
            * surface_id (int, optional): specific surface id to extract info from. Defaults to -1.
                If none is provided it will default to -1 where we extract and save to memory info
                from all surfaces. If running in parallel its better to specify the surface
                so we only extract and store limited amount of information.
            * save_dir (str, optional): directory to save csv to. Defaults to None.
        """
        # TODO set up such that we can pass in a path of stats the user wants and we filter final csv accordingly
        self.ims_file_path = ims_file_path
        self.surface_id = surface_id
        self.save_dir = save_dir
        self.ims = ImarisDataObject(self.ims_file_path)
        self._configure_instance(surface_id=surface_id)

        del self.ims
        gc.collect()

        # new addition
        self.filename = os.path.basename(ims_file_path).split(".")[0]

    def _configure_instance(self, surface_id: int) -> None:
        """
        * Extracts relevant information from ims object and
        instantiates it as instance variables for fast recall.

        Args:
            surface_id (int): specific surface id to extract info from. ZERO INDEXED

        Currently Extracts:
            - all the surface names -- List
            - all the stats_names -- {id: pd.DataFrame}
            - all the stats values -- {id: pd.DataFrame}
            - all the factor info -- {id: pd.DataFrame}
        """
        # extract all information and saves it as a instance var
        if surface_id == -1:  # configure all available surfaces
            self.surface_names = self.ims.get_object_names("Surface")
        else:
            # grab the surface we care about
            self.surface_names = self.ims.get_object_names("Surface")
            if (surface_id >= 0) and (surface_id < len(self.surface_names)):
                self.surface_names = [self.surface_names[surface_id]]
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
        }

        # get all the stats values for every surface {surf_id: stats_values_df}
        self.stats_values = {
            surface_id: self.ims.get_stats_values(surface_name)
            for surface_id, surface_name in enumerate(self.surface_names)
        }

        # get all the factor table info for every surface {surf_id: factor_df}
        self.factors = {
            surface_id: self.ims.get_object_factor(surface_name)
            for surface_id, surface_name in enumerate(self.surface_names)
        }

        # gets all the track id information for every spot
        self.track_ids = {
            surface_id: self.ims.get_track_ids(surface_name)
            for surface_id, surface_name in enumerate(self.surface_names)
        }

        # get all object information for every spot
        self.track_info = {
            surface_id: self.ims.get_track_info(surface_name)
            for surface_id, surface_name in enumerate(self.surface_names)
        }

        self.object_ids = {}
        for surface_id, surface_name in enumerate(self.surface_names):
            if self.ims.contains_tracks(surface_name):
                self.object_ids[surface_id] = self.ims.get_track_object_ids(
                    surface_name
                )
            else:
                self.object_ids[surface_id] = self.ims.get_object_ids(surface_name)

    def _save_csv(
        self,
        dataframe: pd.DataFrame,
        save_dir: str,
        surface_id: int,
    ) -> None:
        # TODO: instead of surface_id, see if we can insert the REAL surface name
        # To do this we can grab all the surface names, and find the one that is missing
        # as the current surface_id. because one is always missing from the factor list
        # and the one that is missing is the name we want.
        # a function to write csv information to disk
        # get save_dir/original_filename.csv
        ims_filename = os.path.basename(self.ims_file_path).split(".")[0]
        ims_filename = f"{ims_filename}_surface_track_object_{(surface_id + 1)}.csv"
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

        # gather info for current surface
        surface_name = self.surface_names[surface_id]
        stat_names = self.stats_names.get(surface_id)
        stat_values = self.stats_values.get(surface_id)
        object_id = self.object_ids.get(surface_id)
        factor = self.factors.get(surface_id)

        # update channel
        stat_names = self._update_channel_info_fast(stat_names, factor)

        # update surface names
        stat_names = self._update_surface_info_fast(stat_names, factor)

        # filter stats values by object ids (ie: ignore info related to trackids)
        stat_values = self._filter_stats(
            stats_values=stat_values,
            filter_col_names=["ID_Object"],
            filter_values=[object_id],
        )

        # organize stats value
        organized_stats = self._organize_stats_fast(stat_values)

        # generate csv
        stats_df = self._format_data(organized_stats, stat_names=stat_names)

        if self.track_ids[surface_id] is not None:
            stats_df = self._update_track_id_info(surface_id, stats_df)

        return stats_df

    def extract_and_save(self, idx: int, save_dir: str = None) -> None:
        # this function is the funtion that gets called externally
        # we can have this function as a ray method to help with distributed execution

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

        # update channel names
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

        # filter stats values by object ids (ie: ignore info related to trackids)
        stat_values = self._filter_stats(
            stats_values=stat_values,
            filter_col_names=["ID_Object"],
            filter_values=[object_id],
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

        # organize stats value
        organized_stats = self._organize_stats_fast(stat_values)
        storage["organized_stats_fast"] = organized_stats

        # generate csv
        stats_df = self._format_data(organized_stats, stat_names=stat_names)
        storage["final_df"] = stats_df

        # add track id information for each object
        if self.track_ids[surface_id] is not None:
            start = time.perf_counter()
            stats_df = self._update_track_id_info(surface_id, stats_df)
            print(f"time update track info: {time.perf_counter() - start}")
            storage["final_df"] = stats_df
        else:
            print(
                f"Surface ID: {surface_id} -- Surface Name: {surface_name} -- Contains No Tracks, Track ID Unavilable."
            )

        return storage


###########################################################################################
###########################################################################################
