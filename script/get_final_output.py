import os
import pandas as pd

"""
Given 2 directories combine the matching name csv files into one
"""


def combine_csv(folder1, folder2, output_folder):
    files1 = os.listdir(folder1)
    files2 = os.listdir(folder2)

    for file1 in files1:
        file1_name, file1_ext = os.path.splitext(file1)
        file2_name = file1_name.replace("_output", "_dyn_output") + ".csv"
        file2_path = os.path.join(folder2, file2_name)
        if os.path.isfile(file2_path):
            df1 = pd.read_csv(os.path.join(folder1, file1))
            df2 = pd.read_csv(file2_path)

            combined_df = pd.concat([df1, df2], axis=1)

            combined_file_name = file1_name + "_final_output.csv"
            combined_file_path = os.path.join(output_folder, combined_file_name)
            combined_df.to_csv(combined_file_path, index=False)
            #print(f"Combined file saved: {combined_file_path}")
        else:
            print(f"No match found in {folder2} for {file2_name}")


# Example usage
folder1 = r"C:\Users\dunca\Desktop\csv_output"
folder2 = r"C:\Users\dunca\Desktop\dyn_output"
output_folder = r"C:\Users\dunca\Desktop\fin_output"

combine_csv(folder1, folder2, output_folder)