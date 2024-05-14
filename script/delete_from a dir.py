import os


"""
Given 2 directories a and b
Delete all the files from b that appear in a
"""

def delete_files_in_directory(dir_a, dir_b):
    files_b = set(os.listdir(dir_b))

    for file_a in os.listdir(dir_a):
        if file_a in files_b:
            file_b_path = os.path.join(dir_b, file_a)
            os.remove(file_b_path)
            print(f"Deleted {file_a} from {dir_b}")


# Example usage:
dir_a = r"C:\Users\dunca\Desktop\done_samples"
dir_b = r"C:\Users\dunca\Desktop\b"
delete_files_in_directory(dir_a, dir_b)