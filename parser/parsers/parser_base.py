import pandas as pd
from functools import partial
from typing import Dict, List
from abc import ABC, abstractmethod


################################################################################################
################################################################################################
class Parser(ABC):
    def _organize_stats_fast(self, stats_values: pd.DataFrame) -> Dict:
        """Organized the data such that it looks like
        {ID_Object: {Stats Name: Value}}

        Args:
            stats_values (pd.DataFrame): a single dataframe
            that contains the statistics for a single spot

        Returns:
            Dict: _description_
        """
        grouped_stats = {
            obj_id: dict(zip(sub.ID_StatisticsType, sub.Value))
            for obj_id, sub in stats_values.groupby("ID_Object")
        }
        return grouped_stats

    def _format_data(
        self,
        stats_values: Dict,
        stat_names: pd.DataFrame,
    ) -> pd.DataFrame:
        """_summary_

        Args:
            organized_stats (Dict): _description_

        Returns:
            pd.DataFrame: _description_
        """
        # create a dict that maps stat_id to stat_name
        column_names_dict = dict(zip(stat_names["ID"], stat_names["Name"]))
        dataframe = pd.DataFrame(stats_values).transpose()

        # replaces id columns with respective stat name and add idx
        dataframe = dataframe.rename(column_names_dict, axis=1)
        dataframe["Object_ID"] = dataframe.index
        return dataframe

    def _filter_stats(
        self,
        stats_values: pd.DataFrame,
        filter_col_names: List[str],
        filter_values: List[pd.Series],
    ) -> pd.DataFrame:
        """
        Filters the stats values dataframe. It keeps information
        from col_names and filter_values that is passed in as arguments.
        For time step parser, we need to return all the stats for objects
        in a surface that belong to a particular time index.

        Args:
            stats_values (pd.DataFrame): _description_
            filter_col_name (str): name of the column we want to use to filter
            filter_values (str): values that we want to keep

        Returns:
            pd.DataFrame: _description_
        """
        # first filter stats values by object id
        for col_names, values in zip(filter_col_names, filter_values):
            stats_values = stats_values[stats_values[col_names].isin(values)]

        return stats_values

    def _update_channel_info_fast(
        self,
        stats_names: pd.DataFrame,
        factor: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Updates the channel information for the relavent rows
        based on th ID_FactorList information in stats_names

        Args:
            stats_names (pd.DataFrame): _description_
            factor (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """

        channel_map = (
            factor.loc[factor["Name"] == "Channel", ["ID_List", "Level"]]
            .set_index("ID_List")["Level"]
            .to_dict()
        )

        stats_names["Channel_Level"] = stats_names["ID_FactorList"].map(channel_map)

        stats_names["Name"] = stats_names.apply(
            lambda row: (
                f"{row['Name']} Channel_{int(row['Channel_Level'])}"
                if pd.notna(row["Channel_Level"])
                else row["Name"]
            ),
            axis=1,
        )

        stats_names = stats_names.drop(columns="Channel_Level")

        return stats_names

    def _update_surface_info_fast(
        self,
        stats_names: pd.DataFrame,
        factor: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Updates the channel information for the relavent rows
        based on th ID_FactorList information in stats_names

        Args:
            stats_names (pd.DataFrame): _description_
            factor (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """

        # Build mapping from ID_List -> Level for Surfaces
        surface_map = (
            factor.loc[factor["Name"] == "Surfaces", ["ID_List", "Level"]]
            .set_index("ID_List")["Level"]
            .to_dict()
        )

        # Map surface levels to stats_names
        stats_names["Surface_Level"] = stats_names["ID_FactorList"].map(surface_map)

        # Update Name column: append surface level if exists
        stats_names["Name"] = stats_names.apply(
            lambda row: (
                f"{row['Name']}_{row['Surface_Level']}"
                if pd.notna(row["Surface_Level"])
                else row["Name"]
            ),
            axis=1,
        )

        # Drop the helper column
        stats_names = stats_names.drop(columns="Surface_Level")

        return stats_names

    def _update_image_level_info_fast(
        self,
        stats_names: pd.DataFrame,
        factor: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Updates the channel information for the relavent rows
        based on th ID_FactorList information in stats_names

        Args:
            stats_names (pd.DataFrame): _description_
            factor (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """

        # Build mapping from ID_List -> Level for Surfaces
        image_level_map = (
            factor.loc[factor["Name"] == "Image", ["ID_List", "Level"]]
            .set_index("ID_List")["Level"]
            .to_dict()
        )

        # Map surface levels to stats_names
        stats_names["Image_Level"] = stats_names["ID_FactorList"].map(image_level_map)

        # Update Name column: append surface level if exists
        stats_names["Name"] = stats_names.apply(
            lambda row: (
                f"{row['Name']} {row['Image_Level']}"
                if pd.notna(row["Image_Level"])
                else row["Name"]
            ),
            axis=1,
        )

        # Drop the helper column
        stats_names = stats_names.drop(columns="Image_Level")

        return stats_names

    def _update_depth_level_info_fast(
        self,
        stats_names: pd.DataFrame,
        factor: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Updates the channel information for the relavent rows
        based on th ID_FactorList information in stats_names

        Args:
            stats_names (pd.DataFrame): _description_
            factor (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """

        # Build mapping from ID_List -> Level for Surfaces
        depth_level_map = (
            factor.loc[factor["Name"] == "Depth", ["ID_List", "Level"]]
            .set_index("ID_List")["Level"]
            .to_dict()
        )

        # Map surface levels to stats_names
        stats_names["Depth_Level"] = stats_names["ID_FactorList"].map(depth_level_map)

        # Update Name column: append surface level if exists
        stats_names["Name"] = stats_names.apply(
            lambda row: (
                f"{row['Name']} Depth_{int(row['Depth_Level'])}"
                if pd.notna(row["Depth_Level"])
                else row["Name"]
            ),
            axis=1,
        )

        # Drop the helper column
        stats_names = stats_names.drop(columns="Depth_Level")

        return stats_names

    def _update_level_info_fast(
        self,
        stats_names: pd.DataFrame,
        factor: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Updates the channel information for the relavent rows
        based on th ID_FactorList information in stats_names

        Args:
            stats_names (pd.DataFrame): _description_
            factor (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """

        # Build mapping from ID_List -> Level for Surfaces
        level_map = (
            factor.loc[factor["Name"] == "Level", ["ID_List", "Level"]]
            .set_index("ID_List")["Level"]
            .to_dict()
        )

        # Map surface levels to stats_names
        stats_names["Level"] = stats_names["ID_FactorList"].map(level_map)

        # Update Name column: append surface level if exists
        stats_names["Name"] = stats_names.apply(
            lambda row: (
                f"{row['Name']} Level_{int(row['Level'])}"
                if pd.notna(row["Level"])
                else row["Name"]
            ),
            axis=1,
        )

        # Drop the helper column
        stats_names = stats_names.drop(columns="Level")

        return stats_names

    def _update_track_id_info(self, spot_name, dataframe) -> pd.DataFrame:
        """
        Creates a new column where for each object ID it indicates which track it belongs to.

        Args:
            spot_name (int): name of the spot ie: "Points0"
            dataframe (pd.DataFrame): formatted dataframe with all the stats.

        Returns:
            pd.DataFrame: dataframe with updated Track_ID column.
        """

        object_ids = self.object_ids.get(spot_name)
        track_info = self.track_info.get(spot_name)

        # temp function to handle the case where when we perform
        # apply and an object id is missing we simply just
        # leave it empty
        def _update_object_with_track_id(database, x):
            try:
                return database[int(x["Object_ID"].item())]
            except KeyError:
                return None

        # create database to make obj to track matching efficient
        # key = numerical object id value = track id the obj belong to
        database = {}
        for idx in range(len(track_info)):
            data = track_info.iloc[idx]
            start = data["IndexTrackObjectBegin"]
            end = data["IndexTrackObjectEnd"]
            track_id = data["ID"]
            for i in range(start, end):
                obj_id = object_ids.iloc[i]
                database[obj_id] = track_id

        func = partial(_update_object_with_track_id, database)
        dataframe["Track_ID"] = dataframe.apply(
            func=func,
            axis=1,
        )

        return dataframe

    def _drop_unwanted_stats(self):
        """
        Drops stats not contained in the user defined list of stats names
        from the final csv before saving to disk.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abstractmethod
    def _save_csv(self):
        pass

    @abstractmethod
    def _process(self):
        # a function to to run a end to end pipeline on a single entity
        # in most cases its and end to end data extraction, organization and saving
        pass

    @abstractmethod
    def _configure_instance(self):
        pass

    @abstractmethod
    def inspect(self):
        pass


################################################################################################
################################################################################################
