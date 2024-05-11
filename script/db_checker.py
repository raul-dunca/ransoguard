import hashlib
import os

"""
This script checks for duplicate signature of file in a directory
if a duplicate is found then the duplicate is deleted
"""




def file_signature(file_path, hash_algorithm='sha256'):
    with open(file_path, 'rb') as f:
        hasher = hashlib.new(hash_algorithm)
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicate_signatures(file_paths):
    signatures_seen = set()
    duplicates = set()

    for file_path in file_paths:
        signature = file_signature(file_path)
        if signature in signatures_seen:
            duplicates.add((signature, file_path))
        else:
            signatures_seen.add(signature)

    return duplicates

def remove_duplicates(duplicates):
    for signature, file_path in duplicates:
        os.remove(file_path)

directory = r"C:\Users\dunca\Desktop\a"
file_names = os.listdir(directory)
input_files = [os.path.join(directory, file) for file in file_names]

duplicate_signatures = find_duplicate_signatures(input_files)

if duplicate_signatures:
    print("Duplicate signatures found. Deleting duplicates...")
    remove_duplicates(duplicate_signatures)
    print("Duplicates deleted.")
else:
    print("No duplicate signatures found.")
