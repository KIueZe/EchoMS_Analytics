#！/usr/bin/env python
# coding: utf-8


'''
    @ Junsu Zhou, 2024-11-03
    @ Usage: This scripts can extract well and area data into csv file for further analysis, and output heatmaps.
'''

import os
from glob import glob
from echoms_txt2csv import txt2csv, askfile_ui
from draw_heatmap import draw_heatmap, estimate_plate_type


def main():

    FilePaths = askfile_ui()

    for file in FilePaths:
        file_dir : str = txt2csv(file)
        print(f"Converting {os.path.basename(file)} to csv file...")
        for csv_file in glob(file_dir + '/*.csv'):
            plate_type = estimate_plate_type(csv_file)
            draw_heatmap(plate_type=plate_type, csv_file_path=csv_file)
            print(f"Drawing heatmap for {os.path.basename(csv_file)}...")
    print("Done!")


if __name__ == '__main__':
    main()
    