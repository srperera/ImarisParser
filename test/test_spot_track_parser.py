import sys

sys.path.append("../parser")
import os
import csv
import glob
import pandas as pd
from typing import Tuple
from termcolor import colored
from parsers.spot_track_parser import SpotTrackParserDistributed


################################################################################################
################################################################################################
def get_stats_df(path: str) -> Tuple[str, pd.DataFrame]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        dataframe = []
        for row in reader:
            dataframe.append(row)

    # get the stats name
    stat_name = dataframe[1][0]

    # the first three rows from imaris export needs to be dropped
    dataframe = pd.DataFrame(dataframe[4:], columns=dataframe[3])
    # out = {stat_name: dataframe}
    return (stat_name, dataframe)


################################################################################################
################################################################################################
def get_original_stat_name(column_names, stats_names):
    for name in column_names:
        if name in stats_names:
            return name
    return ValueError("Column Names are Not in stats_name")


################################################################################################
################################################################################################
if __name__ == "__main__":

    # test ims file path
    test_ims_file = "/home/shehan/Documents/projects/nih/projects/ImarisParser/data/imaris_parser_test_files/Spots/KO Sec1 Roi1 3x3 80min.ims"

    # parser
    print("[info] Loading Imaris File")
    parser = SpotTrackParserDistributed(test_ims_file)

    print("[info] Calculating Statistics")
    out = parser.inspect(1)
    parser_df = out["final_df"]
    parser_stat_names = list(parser_df.columns)
    stats_names = out["stat_names_raw"]
    stats_names = list(set(stats_names["Name"]))

    # track stats files
    print("[info] Gathering Ground Truth Files")
    track_stats_dir = "/home/shehan/Documents/projects/nih/projects/ImarisParser/data/imaris_parser_test_files/Spots/KO Sec1 Roi1 3x3 80min-testtracks_Statistics"
    track_stats_files = glob.glob(os.path.join(track_stats_dir, "*.csv"))

    # get all the stat from the test files into a dict
    print("[info] Extracting Ground Truth Data ... ")
    test_stats_dict = {}
    for stat_test_path in track_stats_files:
        items = get_stats_df(stat_test_path)
        if items[0] in test_stats_dict.keys():
            raise ValueError
        else:
            test_stats_dict[items[0]] = items[1]

    # loop over all the stat names we have in our parser
    print("[info] Verifying Parser Output with Ground Truth ...")
    drop_columns = [
        "Unit",
        "Category",
        "Time",
        "Channel",
        "Image",
        "",
        "Collection",
        "Spots",
    ]
    passed_count = 0
    total = 0
    omitted_stats = []
    for stat_name in parser_stat_names:
        try:
            if stat_name not in ["Track_ID", "Time", "Time Index", "Object_ID"]:

                # get the stats df that we are using for validation
                gt_stats_df = test_stats_dict[stat_name]

                # we need to filter out irrelevant columns such as Unit, Category, Time, etc
                # we should only keep the statistics name, track id and object id
                # process gt
                for column in drop_columns:
                    if column in gt_stats_df.columns:
                        gt_stats_df = gt_stats_df.drop(columns=column)

                # get the valid stats name from the gt_stats_file
                valid_stat_name = get_original_stat_name(
                    gt_stats_df.columns, stats_names
                )

                # keep the track and object ids if present
                pred_filtered = []
                if "TrackID" in gt_stats_df.columns and "ID" in gt_stats_df.columns:
                    track_id_series = parser_df["Track_ID"]
                    track_id_series.name = "TrackID"
                    object_id_series = parser_df["Object_ID"]
                    object_id_series.name = "ID"
                    pred_filtered.append(track_id_series)
                    pred_filtered.append(object_id_series)
                elif "ID" in gt_stats_df.columns:
                    # Here Track_ID in ours = ID
                    track_id_series = parser_df["Track_ID"]
                    track_id_series.name = "ID"
                    pred_filtered.append(track_id_series)

                # get the stats for the current stats_name
                pred_filtered.append(parser_df[stat_name])

                # if the stat name is not the same as valid_stat_name
                # we need to modify it
                stat_name_new = None
                if stat_name != valid_stat_name:
                    stat_name_new = stat_name[: len(valid_stat_name)]

                # stack
                pred_filtered_df = pd.concat(pred_filtered, axis=1)

                # change decimal format
                pred_filtered_df[stat_name] = (
                    pred_filtered_df[stat_name].astype(float).map(lambda x: f"{x:.3f}")
                )

                # rename the new columns
                if stat_name_new:
                    pred_filtered_df = pred_filtered_df.rename(
                        columns={stat_name: stat_name_new}
                    )

                # convert whole df to string
                pred_filtered_df = pred_filtered_df.astype(str)

                # reorder columns
                pred_filtered_df = pred_filtered_df[gt_stats_df.columns]

                # reset index
                pred_filtered_df = pred_filtered_df.reset_index(drop="index")

                # compare the two
                match = gt_stats_df.equals(pred_filtered_df)
                if not match:
                    # print(f"Error: Stats for Name {stat_name} Does Not Match")
                    pass
                else:
                    # print(f"Pass: Stats for {stat_name}")
                    passed_count += 1

                total += 1

        except Exception as e:
            print(f"[error] - Test raised exception {e} at stat name {stat_name}")

    if passed_count != total:
        print(
            colored(
                f"Test FAILED only passed {passed_count}/{total} tests",
                "red",
                attrs=["bold"],
            )
        )
    else:
        print(
            colored(
                f"All statistics values match -- Test PASSED -- {passed_count}/{total} tests",
                "green",
                attrs=["bold"],
            )
        )

################################################################################################
################################################################################################
