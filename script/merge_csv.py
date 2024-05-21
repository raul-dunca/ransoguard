import csv
import os

"""
This script given a directory will merge all the csv in that directory
"""

def csv_to_dict(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return next(reader, {})

def merge_csv_files(input_files, output_file):
    fieldnames = set()
    data_dicts = []


    for csv_file in input_files:
        data_dict = csv_to_dict(csv_file)
        fieldnames.update(data_dict.keys())
        data_dicts.append(data_dict)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
        writer.writeheader()
        for data_dict in data_dicts:
            # Fill missing fields with zeros
            for field in fieldnames:
                if field not in data_dict:
                    data_dict[field] = '0'
            writer.writerow(data_dict)

directory = r"C:\Users\dunca\Desktop\batch2"
output_file=r"C:\Users\dunca\Desktop\all_2\all_batch2.csv"

files_names = os.listdir(directory)

input_files = [os.path.join(directory, file) for file in files_names]

merge_csv_files(input_files, output_file)
