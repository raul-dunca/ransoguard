import pandas as pd

"""
This script creates a subset of the main database by
keeping only the best features
"""


def read_best_features(filename):
    features_to_keep = set()

    with open(filename, 'r') as file:
        lines = file.readlines()
    for line in lines:
        parts = line.split()
        if len(parts) < 2:
            print("HOW!?")
            print(line)
            continue

        try:
            feature = parts[1].strip()
            features_to_keep.add(feature)
        except ValueError:
            continue

    return features_to_keep


filename = r"all_features.txt"

best_features=read_best_features(filename)
print(len(best_features))
print(best_features)

best_features_list = list(best_features)
best_features_list.append("label")
df = pd.read_csv(r"C:\Users\dunca\Desktop\all_combined\aa.csv", usecols=best_features_list)



df.to_csv(r"C:\Users\dunca\Desktop\total_out\final_db.csv", index=False)

print(df.head())