import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from echoms_txt2csv import generate_384_plate_positions
# import string


def generate_384_csv_file():

    """
    This is the main function that generates the echo384_data.csv file.
    """

    # generate family name, plate positions, hit values
    family = np.ndarray.tolist(np.repeat(['1'], 384))
    plate_positions = generate_384_plate_positions()
    hit = np.ndarray.tolist(np.repeat(['TRUE'], 384))
    
    # Combine the above lists into a dataframe
    df = pd.DataFrame({'family': family, 'Target_well': plate_positions, 'HIT': hit})
    # Save the dataframe as a csv file
    df.to_csv('echo384_data.csv', index=False)


def draw_384():
    # set up the figure
    plt.figure(figsize=(12, 8))

    # generate the grid
    for i in range(1, 25):
        for j in range(1, 17):
            rect = plt.Rectangle((i-1, j-1), 1, 1, fill=None, edgecolor='black')
            plt.gca().add_patch(rect)

    # set x ticks at the top
    plt.gca().xaxis.tick_top()
    plt.xticks(np.arange(0.5, 24.5, 1), range(1, 25))
    # set y ticks at the left
    plt.gca().yaxis.tick_left()
    plt.yticks(np.arange(0.5, 16.5, 1), [chr(i) for i in range(80, 64, -1)])

    # set the axis limits, title
    plt.xlim(0, 24)
    plt.ylim(0, 16)
    # plt.xlabel('Columns')
    # plt.ylabel('Rows')
    plt.title('384-well plate', 
              fontdict={'family':'Arial', 'size': 20, 'weight': 'bold'}, 
              linespacing=5, pad=32)

    plt.savefig('384_well_plate.png', dpi=150)

    # show the plot
    plt.show()
    

def main():

    generate_384_csv_file()
    draw_384()


if __name__ == '__main__':
    main()