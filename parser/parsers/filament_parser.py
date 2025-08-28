import gc
import os
import pandas as pd
from typing import Dict
from copy import deepcopy
from .parser_base import Parser
from imaris.imaris import ImarisDataObject
from imaris.exceptions import NoFilamentsException


################################################################################################
################################################################################################
class FilamentParserDistributed(Parser):
    """
    Extracts Filament Level Information From Imaris File.
    This class extracts all the individual objects contained in each filament.

    Args:
        Parser (ABCMeta): Parser Abstract Base Class
    """

    def __init__(
        self,
        ims_file_path: str,
        filament_id: int = -1,
        save_dir: str = None,
        **kwargs,
    ) -> None:
        """
        Args:
            * ims_file_path (str): path to .ims file
            * filament_id (int, optional): specific filament id to extract info from. Defaults to -1.
                If none is provided it will default to -1 where we extract and save to memory info
                from all filaments. If running in parallel its better to specify the filament
                so we only extract and store limited amount of information.
            * save_dir (str, optional): directory to save csv to. Defaults to None.
        """
        # TODO set up such that we can pass in a path of stats the user wants and we filter final csv accordingly
        self.ims_file_path = ims_file_path
        self.filament_id = filament_id
        self.save_dir = save_dir
        self.ims = ImarisDataObject(self.ims_file_path)
        self._configure_instance(filament_id=filament_id)

        del self.ims
        gc.collect()

        # new addition
        self.filename = os.path.basename(ims_file_path).split(".")[0]

    def _configure_instance(self, filament_id: int) -> None:
        """
        * Extracts relevant information from ims object and
        instantiates it as instance variables for fast recall.

        Args:
            filament_id (int): specific filament id to extract info from. ZERO INDEXED

        Currently Extracts:
            - all the filament names -- List
            - all the stats_names -- {id: pd.DataFrame}
            - all the stats values -- {id: pd.DataFrame}
            - all the factor info -- {id: pd.DataFrame}
        """
        # extract all information and saves it as a instance var
        if filament_id == -1:
            # configure all available filaments
            self.filament_names = self.ims.get_object_names("Filaments")
        else:
            # grab the filament we care about,
            self.filament_names = self.ims.get_object_names("Filaments")
            if (filament_id >= 0) and (filament_id < len(self.filament_names)):
                self.filament_names = [self.filament_names[filament_id]]
                if self.filament_names[0] is None:
                    raise NoFilamentsException
            elif filament_id >= len(self.filament_names):
                raise ValueError(
                    f"filament_id {filament_id} exceeds number of filaments available"
                )
            else:
                # some currently unknown error
                raise NotImplementedError

        assert type(self.filament_names) == list, "filament_names should be a list"

        # get all the stats names for every filament {surf_id: stats_name_df}
        self.stats_names = {
            filament_id: self.ims.get_stats_names(filament_name)
            for filament_id, filament_name in enumerate(self.filament_names)
            if filament_name is not None
        }

        # get all the stats values for every filament {surf_id: stats_values_df}
        self.stats_values = {
            filament_id: self.ims.get_stats_values(filament_name)
            for filament_id, filament_name in enumerate(self.filament_names)
            if filament_name is not None
        }

        # get all the factor table info for every filament {surf_id: factor_df}
        self.factors = {
            filament_id: self.ims.get_object_factor(filament_name)
            for filament_id, filament_name in enumerate(self.filament_names)
            if filament_name is not None
        }

        # get all the factor table info for every filament {surf_id: factor_df}
        self.object_ids = {
            filament_id: self.ims.get_object_ids(filament_name)
            for filament_id, filament_name in enumerate(self.filament_names)
            if filament_name is not None
        }

    def _save_csv(
        self,
        dataframe: pd.DataFrame,
        save_dir: str,
        filament_id: int,
    ) -> None:
        # TODO: instead of filament_id, see if we can insert the REAL filament name
        # To do this we can grab all the filament names, and find the one that is missing
        # as the current filament_id. because one is always missing from the factor list
        # and the one that is missing is the name we want.
        # a function to write csv information to disk
        # get save_dir/original_filename.csv
        ims_filename = os.path.basename(self.ims_file_path).split(".")[0]
        ims_filename = f"{ims_filename}_filament_{(filament_id + 1)}.csv"
        save_filepath = os.path.join(save_dir, ims_filename)
        dataframe.to_csv(save_filepath)

        # store ims_filename
        self.ims_filename = ims_filename

    def _process(self, filament_id: int) -> None:
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
        if (self.filament_id != -1) and (filament_id != 0):
            raise ValueError(
                f"class is initialized with 1 filament, filament_id should be set to 0"
            )

        # check 2
        if filament_id > len(self.filament_names):
            raise ValueError(
                f"filament_id {filament_id} exceeds number of filaments available {len(self.filament_names)}"
            )

        # gather info for current surface
        filament_name = self.filament_names[filament_id]
        stat_names = self.stats_names.get(filament_id)
        stat_values = self.stats_values.get(filament_id)
        object_id = self.object_ids.get(filament_id)
        factor = self.factors.get(filament_id)

        # update channel
        stat_names = self._update_channel_info_fast(stat_names, factor)

        # update image level information
        stat_names = self._update_image_level_info_fast(stat_names, factor)

        # update image depth level information
        stat_names = self._update_depth_level_info_fast(stat_names, factor)

        # update level information
        stat_names = self._update_level_info_fast(stat_names, factor)

        # filter stats values by object ids (ie: ignore info related to trackids)
        stat_values = self._filter_stats(
            stats_values=stat_values,
            filter_col_names=["ID_Object"],
            filter_values=[object_id],
        )

        # organize stats value (most compute used here)
        organized_stats = self._organize_stats_fast(stat_values)

        # generate csv
        stats_df = self._format_data(organized_stats, stat_names=stat_names)

        return stats_df

    def extract_and_save(self, idx: int, save_dir: str = None) -> None:
        # this function is the funtion that gets called externally
        # we can have this function as a ray method to help with distributed execution
        # self._configure_instance(filament_id=filament_id)
        # del self.ims
        # gc.collect()

        # process filament
        dataframe = self._process(filament_id=idx)

        # adjust filament_id based on init mode
        # save filament
        save_dir = save_dir if save_dir else self.save_dir
        if self.filament_id == -1:
            self._save_csv(dataframe, save_dir, filament_id=idx)
        else:
            self._save_csv(dataframe, save_dir, filament_id=self.filament_id)

        # print(f"[info] -- finished: {self.ims_filename}")

    def inspect(self, filament_id: int) -> Dict:
        """
        Runs a single end to end parser pipeline on a single filament
        and returns all components as a dict.
        Steps:
            - get stat names for a single filament
            - get stat values for a single filament
            - filter stat values to keep only track ids
            - filter stats values to remove track level stat information
            - rename certian columns (if needed)(need a custom func for this to add channel info)
            - organize the filtered stats
            - generate csv
            - save csv

        Args:
            filament_id (int): _description_
        """
        # check 1
        if (self.filament_id != -1) and (filament_id != 0):
            raise ValueError(
                f"class is initialized with 1 filament, filament_id should be set to 0"
            )

        # check 2
        if filament_id > len(self.filament_names):
            raise ValueError(
                f"filament_id {filament_id} exceeds number of filaments available {len(self.filament_names)}"
            )

        # dict to hold all values to be returned for inspection
        storage = {}

        # gather info for current filament
        filament_name = self.filament_names[filament_id]
        storage["filament_name"] = filament_name
        stat_names = self.stats_names.get(filament_id)
        storage["stat_names_raw"] = deepcopy(stat_names)
        stat_values = self.stats_values.get(filament_id)
        storage["stat_values_raw"] = stat_values
        object_id = self.object_ids.get(filament_id)
        storage["object_id"] = object_id
        factor = self.factors.get(filament_id)
        storage["factor"] = factor

        # update channel information
        stat_names = self._update_channel_info_fast(
            stats_names=stat_names, factor=factor
        )
        storage["stat_names_channel_info"] = stat_names

        # update image level information
        stat_names = self._update_image_level_info_fast(
            stats_names=stat_names, factor=factor
        )
        storage["stat_names_image_info"] = stat_names

        # update image depth level information
        stat_names = self._update_depth_level_info_fast(
            stats_names=stat_names, factor=factor
        )
        storage["stat_names_depth_info"] = stat_names

        # update level information
        stat_names = self._update_level_info_fast(stats_names=stat_names, factor=factor)
        storage["stat_names_filament_info"] = stat_names

        # filter stats values by object ids (ie: ignore info related to trackids)
        stat_values = self._filter_stats(
            stats_values=stat_values,
            filter_col_names=["ID_Object"],
            filter_values=[object_id],
        )
        storage["stat_values_filtered"] = stat_values

        # organize stats value
        organized_stats = self._organize_stats_fast(stat_values)
        storage["organized_stats"] = organized_stats

        # generate csv
        stats_df = self._format_data(organized_stats, stat_names=stat_names)
        storage["final_df"] = stats_df

        return storage


################################################################################################
################################################################################################
