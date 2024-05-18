import json
import re
import shutil
import subprocess
import time

import requests
import os

from dotenv import load_dotenv

"""
This script is used to give a label for a sample
"""


def run_avclass(file_path):
    """
    executes floss on the file_path and error handles it
    """
    command = "avclass -f " +file_path
    result = subprocess.run(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode !=0:
        return None, result.stderr.decode('utf-8')
    else:
        output = result.stdout.decode('utf-8')
        left_side = []
        right_side = []
        parts = output.split('\t',1)
        left_side.append(parts[0].strip())
        if len(parts) > 1:
            right_side.append(parts[1].strip())
        else:
            right_side.append('')

        if right_side[0]=='-\t[]':
            right_side[0]='[]'
        special_characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        label=right_side[0]
        for char in special_characters:
            label = label.replace(char, '')                         #delete unallowed chars in directory names

        return left_side[0], label



def main():

    directory_path = r"C:\Users\dunca\Desktop\done_samples"                   #TODO Change this
    json_putput=r"C:\Users\dunca\Desktop\json"                                #TODO Change this
    classification_path=r"C:\Users\dunca\Desktop\classification"              #TODO Change this

    last_call_time = 0
    file_list = os.listdir(directory_path)

    label_counter = {}
    all=len(file_list)
    cnt=1
    for filename in file_list:


        print("Working on "+filename)
        print(str(cnt)+"/"+str(all))
        cnt+=1

        output_file_path = os.path.join(json_putput, filename + "_output.json")

        if os.path.exists(output_file_path):
            file_path = os.path.join(directory_path, filename)


            signiture,lable=run_avclass(output_file_path)


            if signiture is None:
                print("Error: " +filename +" " + lable)
            else:
                if lable not in label_counter:
                    label_counter[lable]=1
                    lable_dir=os.path.join(classification_path,lable)
                    os.makedirs(lable_dir)
                else:
                    label_counter[lable]+=1
                    lable_dir = os.path.join(classification_path, lable)

                destination_file_path = os.path.join(lable_dir, filename)
                shutil.copy(file_path, destination_file_path)

    print(label_counter)



if __name__ == "__main__":
    main()
