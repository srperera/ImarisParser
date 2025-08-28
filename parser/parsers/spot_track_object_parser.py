import gc
import os
import time
import pandas as pd
from typing import Dict
from copy import deepcopy
from .parser_base import Parser
from imaris.imaris import ImarisDataObject
from imaris.exceptions import NoSpotException


###########################################################################################
###########################################################################################
class SpotTrackObjectParserDistributed(Parser):
    """
    Extracts all the individual cells or spots in a given Spot Track.
    This class does not extract track level information just the individual objects that belong to each Spot Track.

    Args:
        Parser (ABCMeta): Parser Abstract Base Class
    """

    def __init__(
        self,
        ims_file_path: str,
        spot_id: int = -1,
        save_dir: str = None,
        **kwargs,
    ) -> None:
        # TODO set up such that we can pass in a path of stats the user wants and we filter final csv accordingly
        self.ims_file_path = ims_file_path
        self.spot_id = spot_id
        self.save_dir = save_dir
        self.ims = ImarisDataObject(self.ims_file_path)
        self._configure_instance(spot_id=spot_id)

        del self.ims
        gc.collect()

        # new addition
        self.filename = os.path.basename(ims_file_path).split(".")[0]

    def _configure_instance(self, spot_id: int) -> None:
        """
        Extracts relevant information from ims object and
        instantiates it as instance variables for fast recall.

        Currently Extracts:
            - all the spot names -- List
            - all the stats_names -- {id: pd.DataFrame}
            - all the stats values -- {id: pd.DataFrame}
            - all the factor info -- {id: pd.DataFrame}

        Args:
            spot_id (int): index of the spot ["points0", "points1"]
                spot_id = 0 is information on "points0" etc

        """
        # extract all information and saves it as a instance var
        if spot_id == -1:
            # configure all available spots
            self.spot_names = self.ims.get_object_names("Points")
        else:
            # grab the single spot we care about
            self.spot_names = self.ims.get_object_names("Points")
            if (spot_id >= 0) and (spot_id <= len(self.spot_names)):
                self.spot_names = [self.spot_names[spot_id]]
                if self.spot_names[0] is None:
                    raise NoSpotException
            elif spot_id > len(self.spot_names):
                raise ValueError(
                    f"spot_id {spot_id} exceeds number of spots available {len(self.spot_names)}"
                )
            else:
                # some currently unknown error
                raise NotImplementedError("currently unknown errror lol")

        # get all the stats names for every spot {spot_id: stats_name_df}
        self.stats_names = {
            spot_id: self.ims.get_stats_names(spot_name)
            for spot_id, spot_name in enumerate(self.spot_names)
            if spot_name is not None
        }

        # get all the stats values for every spot {surf_id: stats_values_df}
        self.stats_values = {
            spot_id: self.ims.get_stats_values(spot_name)
            for spot_id, spot_name in enumerate(self.spot_names)
            if spot_name is not None
        }

        # get all the factor table info for every spot {surf_id: factor_df}
        self.factors = {
            spot_id: self.ims.get_object_factor(spot_name)
            for spot_id, spot_name in enumerate(self.spot_names)
            if spot_name is not None
        }

        # gets all the track id information for every spot
        self.track_ids = {
            spot_id: self.ims.get_track_ids(spot_name)
            for spot_id, spot_name in enumerate(self.spot_names)
            if spot_name is not None
        }

        # get all object information for every spot
        self.track_info = {
            spot_id: self.ims.get_track_info(spot_name)
            for spot_id, spot_name in enumerate(self.spot_names)
            if spot_name is not None
        }

        # get all the track object id information for every spot {surf_id: object_ids_series}
        # self.object_ids = {
        #     spot_id: self.ims.get_track_object_ids(spot_name)
        #     for spot_id, spot_name in enumerate(self.spot_names)
        # }
        # TODO
        self.object_ids = {}
        for spot_id, spot_name in enumerate(self.spot_names):
            if self.ims.contains_tracks(spot_name):
                self.object_ids[spot_id] = self.ims.get_track_object_ids(spot_name)
            else:
                self.object_ids[spot_id] = self.ims.get_object_ids(spot_name)

    def _save_csv(
        self,
        dataframe: pd.DataFrame,
        save_dir: str,
        spot_id: int,
    ) -> None:
        # a function to write csv information to disk
        # get save_dir/original_filename.csv
        ims_filename = os.path.basename(self.ims_file_path).split(".")[0]
        ims_filename = f"{ims_filename}_spot_track_objects_{(spot_id + 1)}.csv"
        save_filepath = os.path.join(save_dir, ims_filename)
        dataframe.to_csv(save_filepath)

        # store ims_filename
        self.ims_filename = ims_filename

    def _process(self, spot_id: int) -> None:
        """
        Runs a single end to end parser pipeline on a single spot
        Steps:
            - get stat names for a single spot
            - get stat values for a single spot
            - filter stat values to keep only track ids
            - filter stats values to remove track level stat information
            - rename certian columns (if needed)(need a custom func for this to add channel info)
            - organize the filtered stats
            - generate csv
            - save csv

        Args:
            spot_id (int): _description_
        """
        # check 1
        if (self.spot_id != -1) and (spot_id != 0):
            raise ValueError(
                f"class is initialized with 1 spot, spot_id should be set to 0"
            )

        # check 2
        if spot_id > len(self.spot_names):
            raise ValueError(
                f"spot_id {spot_id} exceeds number of spots available {len(self.spot_names)}"
            )

        # gather info for current spot
        spot_name = self.spot_names[spot_id]
        stat_names = self.stats_names.get(spot_id)
        stat_values = self.stats_values.get(spot_id)
        object_id = self.object_ids.get(spot_id)
        factor = self.factors.get(spot_id)

        # update channel and spot names
        stat_names = self._update_channel_info_fast(
            stats_names=stat_names, factor=factor
        )

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

        # add track id information for each object
        if self.track_ids[spot_id] is not None:
            stats_df = self._update_track_id_info(spot_id, stats_df)

        return stats_df

    def extract_and_save(self, idx: int, save_dir: str = None) -> None:
        # this function is the funtion that gets called externally
        # we can have this function as a ray method to help with distributed execution
        # check 1

        # process spot
        dataframe = self._process(idx)

        # adjust spot_id based on init mode
        # save spot
        save_dir = save_dir if save_dir else self.save_dir
        if self.spot_id == -1:
            self._save_csv(dataframe, save_dir, spot_id=idx)
        else:
            self._save_csv(dataframe, save_dir, spot_id=self.spot_id)

        # print(f"[info] -- finished: {self.ims_filename}")

    def inspect(self, spot_id: int) -> Dict:
        """
        Runs a single end to end parser pipeline on a single spot
        and returns all components as a dict.
        Steps:
            - get stat names for a single spot
            - get stat values for a single spot
            - filter stat values to keep only track ids
            - filter stats values to remove track level stat information
            - rename certian columns (if needed)(need a custom func for this to add channel info)
            - organize the filtered stats
            - generate csv
            - save csv

        Args:
            spot_id (int): _description_
        """

        # dict to hold all values to be returned for inspection
        storage = {}

        # gather info for current spot
        spot_name = self.spot_names[spot_id]
        storage["spot_name"] = spot_name
        stat_names = self.stats_names.get(spot_id)
        storage["stat_names_raw"] = deepcopy(stat_names)
        stat_values = self.stats_values.get(spot_id)
        storage["stat_values_raw"] = deepcopy(stat_values)
        object_id = self.object_ids.get(spot_id)
        storage["object_id"] = object_id
        factor = self.factors.get(spot_id)
        storage["factor"] = factor

        # update channel names
        # update spot name
        stat_names = self._update_spot_info_fast(stat_names, factor)
        storage["stat_names_channel_info"] = stat_names

        # update channel
        stat_names = self._update_channel_info_fast(stat_names, factor)
        storage["stat_names_channel_info"] = stat_names

        # update img info
        stat_names = self._update_image_level_info_fast(stat_names, factor)
        storage["stat_names_img_info"] = stat_names

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
        # start = time.perf_counter()
        organized_stats = self._organize_stats_fast(stat_values)
        # print(f"time organize stats: {time.perf_counter() - start}")
        storage["organized_stats_fast"] = organized_stats

        # generate csv
        stats_df = self._format_data(organized_stats, stat_names=stat_names)
        storage["stats_df"] = stats_df

        # add track id information for each object
        if self.track_ids[spot_id] is not None:
            # start = time.perf_counter()
            stats_df = self._update_track_id_info(spot_id, stats_df)
            # print(f"time update track info: {time.perf_counter() - start}")
            storage["final_df"] = stats_df
        else:
            print(
                f"Spot ID: {spot_id} -- Spot Name: {spot_name} -- Contains No Tracks, Track ID Unavilable."
            )

        return storage


###########################################################################################
###########################################################################################
