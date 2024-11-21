#！/usr/bin/env python
# coding: utf-8


'''
    @ Junsu Zhou, 2024-11-13
    @ Usage: This script reads a CSV file containing the area values for each well in a 384-well Echo384 plate.
'''


import numpy as np
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
import sys


def askfile_ui() -> tuple:

    # creat object
    root = tk.Tk()
    root.withdraw()

    # set window title
    root.title("Select EchoMS txt files.")

    # FolderPath=filedialog.askdirectory()  # show dialog box and return folder path
    FilePaths = filedialog.askopenfilenames()

    if not FilePaths:
        sys.exit()
    else:
        return FilePaths # return tuple of file paths


def read_table(file_path):
    """
    This function reads a table file containing the area values for each well in a 384-well Echo384 plate, 
    and returns a pandas dataframe.
    """

    df = pd.read_csv(file_path, sep='\t')
    df = df[['Sample Name', 'Component Name', 'Area']]
    df = df.dropna()
    df['Sample Name'] = df['Sample Name'].apply(lambda x: x.split('-')[0])
    df = df.rename(columns={'Sample Name': 'Well'})
    # df['Area'] = df['Area'].apply(lambda x: np.float64(x.replace(',', '.')))
    return df


def generate_dataframes_by_component(df : pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    This function generates a dictionary of dataframes, where each dataframe contains the area values for a specific component component.
    """

    component_dfs = {}
    for component in df['Component Name'].unique():
        component_df = df[df['Component Name'] == component]
        component_dfs[component] = component_df

    return component_dfs


def generate_dataframes_by_quadrants(df : pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    This function generates a dictionary of dataframes, where each dataframe contains the area values for a specific quadrant.
    """
    quadrants = ['A1', 'A2', 'B1', 'B2']
    quadrant_dfs = {}
    df_96 = pd.DataFrame({'Well': generate_96_plate_positions()})


    for quadrant in quadrants:
        quadrant_df = df[df['Well'].isin(generate_384_plate_positions(quadrant=True)[quadrant])]

        # map the 384 wells to the 96 wells in the quadrant
        if len(quadrant_df) == len(df_96):
            quadrant_df = quadrant_df.reset_index(drop=True)
            quadrant_df = pd.concat([df_96.iloc[:, 0], quadrant_df.iloc[:, 1]], axis=1, ignore_index=False)

        quadrant_dfs[quadrant] = quadrant_df

    return quadrant_dfs



def complete_384_wells(df : pd.DataFrame) -> pd.DataFrame:
    """
    This function adds missing 384 wells to the data frame, and removes outlier wells, if necessary.
    """

    plate_positions = generate_384_plate_positions()

    missing_well = set(plate_positions) - set(df['Well'].values)
    outlier_well = set(df['Well'].values) - set(plate_positions)
    
    for well in missing_well:
        df = pd.concat([df, pd.DataFrame({'Well': [well], 'Area': [0]})], ignore_index=True)

    for well in outlier_well:
        df = df[df['Well'] != well]

    # sort the dataframe by well position
    df_sorted = df.sort_values(by='Well', key=lambda x: x.apply(sort_wells))
    df_sorted = df_sorted.reset_index(drop=True)

    return df_sorted


def sort_wells(well: str) -> tuple:
    """
    This function sorts wells by row and column number.
    """
    column, row = well[0], well[1:]
    return (ord(column.upper()) - ord('A') + 1, int(row))


def generate_384_plate_positions(quadrant=False) -> dict or np.ndarray:
    """
    This function generates all possible combinations of rows and columns to get the well positions on a 384-well plate.
    """

    # generate the quadrant positions, row and column numbers
    A1_wells = np.array([f"{chr(ord('A') + i)}{j}" for i in range(0, 16, 2) for j in range(1, 25, 2)])
    A2_wells = np.array([f"{chr(ord('A') + i)}{j}" for i in range(0, 16, 2) for j in range(2, 25, 2)])
    B1_wells = np.array([f"{chr(ord('B') + i)}{j}" for i in range(0, 16, 2) for j in range(1, 25, 2)])
    B2_wells = np.array([f"{chr(ord('B') + i)}{j}" for i in range(0, 16, 2) for j in range(2, 25, 2)])

    # combine the quadrant positions to get the plate positions
    plate_positions = np.concatenate((A1_wells, A2_wells, B1_wells, B2_wells))
    plate_positions = plate_positions.reshape(1, 384)[0]

    if quadrant:
        return {'A1': A1_wells, 'A2': A2_wells, 'B1': B1_wells, 'B2': B2_wells}
    else:
        return plate_positions


def generate_96_plate_positions() -> np.ndarray:
    """
    This function generates all possible combinations of rows and columns to get the well positions on a 96-well plate.
    """
    nine_six_wells = np.array([f"{chr(ord('A') + i)}{j}" for i in range(8) for j in range(1, 13, 1)])

    return nine_six_wells


def txt2csv(file_path: str) -> str:
    """
    This is the main function that calls all the other functions.
    """
    
    df = read_table(file_path)

    file_name = os.path.basename(file_path).replace('.txt', '')
    file_dir = './results' + os.sep + file_name
    os.mkdir(file_dir)

    component_dfs = generate_dataframes_by_component(df)
    for component, component_df in component_dfs.items():
        component_df = complete_384_wells(component_df)
        component_df = component_df[["Well", "Area"]]

        # save component dataframe as csv files
        component_csv_path = file_dir + os.sep + file_name + f'_{component.lower().replace(" ", "_")}.csv'
        component_df.to_csv(component_csv_path, index=False)

        # generate quadrant dataframes as csv files
        for quadrant, quadrant_df in generate_dataframes_by_quadrants(component_df).items():
            quadrant_df.to_csv(file_dir + os.sep + file_name + f'_{component.lower().replace(" ", "_")}_' + quadrant + '.csv', index=False)
    
    return file_dir


if __name__ == '__main__':
    txt2csv()
