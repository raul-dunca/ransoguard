import os
import shutil
import pandas as pd


"""
Script used to delete special chars (unaccepted by Weka) from column names
and then remove any duplicate columns
"""

def clean_column_names(df):
    # Use vectorized string operations to remove non-alphanumeric characters
    df.columns = df.columns.str.replace(r'[^\w.]', '', regex=True)
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def process_csv_files(input_directory, output_directory):
    file_list = [f for f in os.listdir(input_directory) if f.endswith('.csv')]
    all_files = len(file_list)

    for cnt, filename in enumerate(file_list, start=1):
        input_file_path = os.path.join(input_directory, filename)
        output_file_path = os.path.join(output_directory, filename)

        df = pd.read_csv(input_file_path)

        if any(df.columns.str.contains(r'\W')):
            df = clean_column_names(df)
            df.to_csv(output_file_path, index=False)
            print(f"Processed file: {input_file_path} -> Saved to: {output_file_path}")
        else:
            shutil.copy(input_file_path, output_file_path)
            print(f"Copied file: {input_file_path} -> Saved to: {output_file_path}")

        print(f"{cnt}/{all_files}")


if __name__ == "__main__":
    input_directory_path = r"C:\Users\dunca\Desktop\fin_output"
    output_directory_path = r"C:\Users\dunca\Desktop\clean_fin_output"

    process_csv_files(input_directory_path, output_directory_path)


