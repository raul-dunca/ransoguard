import pandas as pd

"""
Used to move label column last (convenient in Weka)
"""

def move_column_to_last(csv_file_path, column_to_move):
    df = pd.read_csv(csv_file_path)

    if column_to_move not in df.columns:
        print(f"Column '{column_to_move}' not found in the CSV file.")
        return

    # Move the specified column label to the last position
    columns = [col for col in df.columns if col != column_to_move] + [column_to_move]
    df = df[columns]

    num_columns = len(df.columns)
    print(f"Number of columns: {num_columns}")

    df.to_csv(csv_file_path, index=False)
    print(f"Column '{column_to_move}' moved to the last position in the CSV file.")

if __name__ == "__main__":
    csv_file_path = r"C:\Users\dunca\Desktop\all_2\all_batch2.csv"
    column_to_move = "label"
    move_column_to_last(csv_file_path, column_to_move)
