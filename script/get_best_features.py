"""
This scrip normalizes the best features from the 2 batches and then
combines them in a single set
"""


def merge_dicts_max(dict1, dict2):
    merged_dict = {}

    for key, value in dict1.items():
        merged_dict[key] = value

    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key] = max(merged_dict[key], value)
        else:
            merged_dict[key] = value

    return merged_dict


def sort_dict_by_values(input_dict):
    sorted_dict = dict(sorted(input_dict.items(), key=lambda item: item[1], reverse=True))

    return sorted_dict


def find_max(dict):
    max = 0
    for key in dict:
        if dict[key] > max:
            max = dict[key]

    return max


def find_min(dict):
    min = 9999999
    for key in dict:
        if dict[key] < min:
            min = dict[key]

    return min


def normalize(dict, maxi, min):
    for key in dict:
        dict[key] = (dict[key] - min) / (maxi - min)

    return dict


def read_names_from_file(filename):
    names_dict = {}

    with open(filename, 'r') as file:
        lines = file.readlines()
    for line in lines:
        parts = line.split()
        if len(parts) < 3:
            print("HOW!?")
            print(line)
            continue

        try:
            nr = float(parts[0])
            name = parts[2].strip()

            if nr > 0:
                names_dict[name] = nr
        except ValueError:
            continue

    return names_dict


filename1 = r"C:\Users\dunca\Desktop\all_1\best_features_clean.txt"
names1 = read_names_from_file(filename1)

max1 = find_max(names1)
min1 = find_min(names1)
cnt1 = 0
for name in names1:
    cnt1 += 1

names1 = normalize(names1, max1, min1)

print(f"Total for file1 is: {cnt1}")
with open("norm_f1.txt", "w+", encoding="utf-8") as f:
    for key in names1:
        f.write(f"{names1[key]} {key} \n")

filename2 = r"C:\Users\dunca\Desktop\all_2\best_features_clean.txt"
names2 = read_names_from_file(filename2)
max2 = find_max(names2)
min2 = find_min(names2)
cnt2 = 0
for name in names2:
    cnt2 += 1
names2 = normalize(names2, max2, min2)
print(f"Total for file2 is: {cnt2}")

with open("norm_f2.txt", "w+", encoding="utf-8") as f:
    for key in names2:
        f.write(f"{names2[key]} {key} \n")

final_dict = merge_dicts_max(names1, names2)

sorted_dict = sort_dict_by_values(final_dict)
print(sorted_dict)

with open("all_features.txt", "w+", encoding="utf-8") as f:
    for key in sorted_dict:
        f.write(f"{sorted_dict[key]} {key} \n")
