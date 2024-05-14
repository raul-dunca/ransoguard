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

def scan_file_with_virustotal(file_path, api_key):
    url = 'https://www.virustotal.com/vtapi/v2/file/scan'
    params = {'apikey': api_key}
    files = {'file': (file_path, open(file_path, 'rb'))}
    response = requests.post(url, files=files, params=params)
    response_json = response.json()
    if 'resource' in response_json:
        resource = response_json['resource']
        return resource
    else:
        print("Error scanning file:", response_json)
        return None

def get_scan_report(file_path, api_key):
    url = 'https://www.virustotal.com/vtapi/v2/file/report'
    params = {'apikey': api_key, 'resource': file_path}
    response = requests.get(url, params=params)
    return response.json()



def handle_rate_limit(last_call_time):                      #for the 4 lookups/min limition on virustotal
    current_time = time.time()
    elapsed_time = current_time - last_call_time
    if elapsed_time < 30:
        time.sleep(30 - elapsed_time)


def main():

    directory_path = r"C:\Users\dunca\Desktop\b"                   #TODO Change this
    json_putput=r"C:\Users\dunca\Desktop\json"                     #TODO Change this
    classification_path=r"C:\Users\dunca\Desktop\classification"   #TODO Change this

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

        file_path = os.path.join(directory_path, filename)

        #quoted_file_path = '"{}"'.format(file_path)
        load_dotenv()
        api_key = os.environ.get("API_KEY")

        resource = scan_file_with_virustotal(file_path, api_key)

        if resource:
            print("File submitted for analysis. Waiting for results...")
            handle_rate_limit(last_call_time)
            report = get_scan_report(resource, api_key)
            # Write report to a JSON file
            with open(output_file_path, 'w+') as outfile:
                json.dump(report, outfile, separators=(',', ':'))
            print("Report saved")
            last_call_time = time.time()
        signiture,lable=run_avclass(output_file_path)

        if signiture is None:
            print("Error:" +lable)
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
