import csv
import os
import pprint


def get_files_with_subdirectories(root_dir):

    for path, subdirs, files in os.walk(root_dir):
        for subdir in subdirs:
            subdir_path=os.path.join(root_dir,subdir)
            for file in os.listdir(subdir_path):
                file_label_dict[file]=subdir


file_label_dict={}
classification_dir = r"C:\Users\dunca\Desktop\classification"
files_info  = get_files_with_subdirectories(classification_dir)

with open ("label_class.txt",'w+') as f:
    pprint.pprint(file_label_dict, stream=f)


# output_dir = r"C:\Users\dunca\Desktop\final_output"
#
# for filename in os.listdir(output_dir):
#
#     file_key = filename.replace("_output_final_output.csv", "")
#
#     if file_key in file_label_dict:
#         label = file_label_dict[file_key]
#
#         with open(os.path.join(output_dir, filename), 'r') as file:
#             reader = csv.reader(file)
#             rows = list(reader)
#
#         headers = rows[0] + ["label"]
#         updated_rows = rows[1]+ [label]
#
#         with open(os.path.join(output_dir, filename), 'w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(headers)
#             writer.writerow(updated_rows)
#
#         print(f"Label added to {filename}")