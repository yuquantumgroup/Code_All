import csv
import os
from os import path

def setup_csv(path, filename, *headers):
    filepath = os.path.join(path, filename)

    ### set headers
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        csvfile.flush()

    return filepath

def write_to_csv(filepath, *data):
    ### write data to csv file
    with open(filepath, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(data)