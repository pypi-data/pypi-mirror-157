# ====================
#  Necessary packages
# ====================

import os
import pandas as pd
from pandas import testing as tm

# ============================
#  Functions for loading data
# ============================

def curate_NPM(path):

    """
    Reads all .NPM.csv files from the input directory and saves
    a new .csv file each RegionXG in the files.

    Parameters
    ----------
    path : str
        directory containing subdirectory (ex. Rat1, Rat2, etc.) which contain .NPM.csv files

    Returns
    -------
    This function does not return variables, but instead saves the read data
    into new .csv files.
    """

    # get the immediate subdirectories of the input path
    sub_dirs = _get_immediate_subdirectories(path)

    # for each sub directory ...
    for sub in sub_dirs:
        sub_path = os.path.join(path, sub)
        NPM_415 = []
        NPM_470 = []

        # for each file in sub directory ...
        for file in os.listdir(sub_path):


            if (file.endswith('.NPM.csv')): # if directory, skip

                display(file)
                # read csv files
                data = pd.read_csv(os.path.join(sub_path, file))
                if 1 in data['LedState'].values: # if Flag contains 17, 415
                    NPM_415 = data

                elif 2 in data['LedState'].values: # if Flag contains 18, 470
                    NPM_470 = data

        if type(NPM_415) == list: # if variable is list (i.e., no dataframe)
            continue

        else:
            # curate and save NPM data
            _curate_NPM_subdir(NPM_415, NPM_470, name=sub, save_path=sub_path)
    return


def _curate_NPM_subdir(NPM_415, NPM_470, name, save_path):

    """
    Helper function combining _curate_and_save_NPM() and _drop_preTTL() functions into one step.

    Parameters
    ----------
    NPM_415 : dataframe
        dataframe containing the 415 data

    NPM_470 : dataframe
        dataframe containing the 470 data

    name : str
        subject name for the data, derived from the subdirectory folder names

    save_path : str
        directory where new .csv files will be saved. This is set to the sub directory by default.

    Returns
    -------
    This function does not return variables, but instead saves the read data
    into new .csv files.
    """

    if 1 not in NPM_415['LedState'].values:
        raise Exception('Flag "17" not found in first input variable. Make sure that 415 and 470 are first and second input variables, respectively.')

    NPM_415_short = _drop_preTTL(NPM_415)
    NPM_470_short = _drop_preTTL(NPM_470)

    _curate_and_save_NPM(NPM_415_short, NPM_470_short, name, save_path)
    return


# Get indexes of TTL (529 or 530 depending in 415 or 470)
#  then get the data from 1 row before first TTL trigger

def _drop_preTTL(NPM_df):

    """
    Helper function that finds the first TTL trigger and drops the data before it.

    Parameters
    ----------
    NPM_df : dataframe
        dataframe containing the either NPM data with Flags.

    Returns
    -------
    NPM_df_short : dataframe
        dataframe without the pre-TTL data and reset indexes.
    """

    TTL_idxs = NPM_df[NPM_df['Input0'] > 0]
    First_TTL = TTL_idxs.index[0]

    NPM_df_short = NPM_df.iloc[First_TTL-1:].reset_index()
    return NPM_df_short


# Curate data and save as one new .csv file per region
def _curate_and_save_NPM(NPM_415_short, NPM_470_short, name, save_path):

    """
    Helper function that takes shortened NPM (dropped preTTL) data and curates the data.
    In short, a new .csv file is created and saved for each RegionXG signal in 415 (Control)
    and 470 (Signal) files.

    Parameters
    ----------
    NPM_415_short : dataframe
        dataframe containing the 415 data that has dropped preTTL data

    NPM_470_short : dataframe
        dataframe containing the 470 data that has dropped preTTL data

    name : str
        subject name for the data, derived from the subdirectory folder names

    save_path : str
        directory where new .csv files will be saved. This is set to the sub directory by default.

    Returns
    -------
    This function does not return variables, but instead saves the read data
    into new .csv file
    """

    regions_415 = NPM_415_short.columns[9:]
    regions_470 = NPM_470_short.columns[9:]
    tm.assert_index_equal(regions_415, regions_470)

    for region in regions_415:

        data_415 = NPM_415_short[region]
        data_470 = NPM_470_short[region]

        region_dict = {'Timestamp': NPM_415_short['Timestamp'],
                   'Signal': data_470,
                   'Control': data_415}

        region_df = pd.DataFrame(data=region_dict)
        region_df = region_df.dropna()

        save_name = name + '_curated_NPM_' + region +'.csv'
        region_df.to_csv(os.path.join(save_path, save_name), index=False)
    return

def _get_immediate_subdirectories(a_dir):

    """
    Helper function that find outputs all immediate subdirectories for a given path.

    Parameters
    ----------
    a_dir : str
        any directory

    Returns
    -------
    sub_dirs : list
        list of all immediate subdirectories
    """

    return [sub_dirs for sub_dirs in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, sub_dirs))]
