#！/usr/bin/env python
# coding: utf-8


'''
    @ Junsu Zhou, 2024-11-13
    @ Usage: This script reads a CSV file containing the area values for each well in a 384-well Echo384 plate, 
             and organizes the data into a 16x24 array, and draws a heatmap of the data.
             The heatmap is saved as a PNG file in the same directory as the CSV file.
'''


import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import seaborn as sns
import pandas as pd
from echoms_txt2csv import askfile_ui

def read_csv(file_path):
    return pd.read_csv(file_path)


def well_position_to_row_col(well_position):
    """
    This function converts a well position (e.g. 'A1') to a row and column number (e.g. (0, 0)).
    """

    well_position = well_position.upper()
    row_letter = well_position[0]
    row_number = ord(row_letter) - ord('A')
    col_number = int(well_position[1:]) - 1

    return (row_number, col_number)


def organize_data(plate_type='384', csv_file_path:str=None):
    """
    This function organizes the data into a (num_rows, num_cols) array.
    for 384, num_rows=16, num_cols=24
    for 96, num_rows=8, num_cols=12
    """

    if plate_type == '384':
        num_rows = 16
        num_cols = 24
    elif plate_type == '96':
        num_rows = 8
        num_cols = 12
    else:
        print('Invalid plate type. Please choose either 384 or 96.')
        return
    
    df = read_csv(csv_file_path)   

    # convert to (num_rows, num_cols) array
    array = np.zeros((num_rows, num_cols))
    for index, row in df.iterrows():
        well_pos = str(row['Well']).upper()
        row_num, col_num = well_position_to_row_col(well_pos)
        # array[row_num, col_num] = row['Area']  # fill in the array with the area values
        array[row_num, col_num] = np.log10(row['Area'] + 1)  # fill in the array with the log10 of area values
    
    return array


def draw_heatmap(plate_type:str='384', csv_file_path:str=None):
    """
    This function draws a heatmap from a CSV file containing the 384 or 96-well plate data.
    """

    if plate_type == '384':
        num_rows = 16
        num_cols = 24
    elif plate_type == '96':
        num_rows = 8
        num_cols = 12
    else:
        print('Invalid plate type. Please choose either 384 or 96.')
        return
    

    # organize the data into a (num_rows, num_cols) array
    array = organize_data(plate_type=plate_type, csv_file_path=csv_file_path)

    # add row and column labels to the data frame
    row_labels = [f'{chr(i+65)}' for i in range(num_rows)]
    col_labels = [f'{i+1}' for i in range(num_cols)]
    df = pd.DataFrame(array, index=row_labels, columns=col_labels)

    # create the seaborn heatmap
    plt.figure(figsize=(16, 9))
    ax = sns.heatmap(df, annot=True, fmt=".2f", cmap="YlGnBu")  
    # annot=True show the values, fmt=".2f" show 2 decimal places
    # coolwarm, YlGnBu, RdBu_r
    # cmap=sns.diverging_palette(20, 220, n=200, as_cmap=True)

    # get the colorbar ticks
    cbar = ax.collections[0].colorbar
    ticks = cbar.get_ticks()

    # set the new ticks with 2 decimal places
    # new_ticks = [f"{val:.0f}" for val in original_ticks]
    new_ticks = [f"{val:.2f} ({(np.power(10, val) - 1):.0f})" for val in ticks]

    # set the new ticks on the colorbar axis
    cbar.ax.yaxis.set_major_locator(ticker.FixedLocator(ticks))
    cbar.ax.yaxis.set_major_formatter(ticker.FixedFormatter(new_ticks))

    # set the colorbar label position and label
    cbar.set_label('log10 values (original values)', labelpad=20)  # labelpad is the distance between the colorbar and the label

    # set the x and y labels
    plt.yticks(rotation='horizontal')
    plt.xticks(rotation='horizontal')

    plt.title(os.path.basename(csv_file_path).replace('.csv', ' ') + 'log10(Area+1)',
            fontdict={'family':'Arial', 'size': 22, 'weight': 'bold'}, 
            linespacing=5, pad=32)

    plt.savefig(csv_file_path.replace('.csv', '.png'), dpi=150)
    # plt.show()


def estimate_plate_type(csv_file_path:str=None):
    """
    This function estimates the plate type (384 or 96) based on the number of rows in the CSV file.
    """

    df = read_csv(csv_file_path)
    num_rows = len(df.index)

    if num_rows == 384:
        return '384'
    elif num_rows == 96:
        return '96'
    else:
        print('Invalid number of rows in the CSV file. Please choose either 384 or 96.')
        return None
    

def main():
    """
    This is the main function that calls all the other functions.
    """

    File_Paths = askfile_ui()
    for file in File_Paths:
        plate_type = estimate_plate_type(csv_file_path=file)
        if plate_type:
            draw_heatmap(plate_type=plate_type, csv_file_path=file)
        else:
            print(f'{file.split("/")[-1]} is invalid plate type. Please choose either 384 or 96 csv file.')


if __name__ == '__main__':
    main()
