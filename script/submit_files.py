import csv
import os

import requests
import time



from dotenv import load_dotenv




"""
This script performs dynamic analysis
"""

def submit_file(file_path, api_key,filename):
    url = "https://www.hybrid-analysis.com/api/v2/submit/file"
    headers = {
        "User-Agent": "Falcon Sandbox",
        "api-key": api_key
    }
    data = {
        "environment_id": 160,              #WINDOWS 10 64 bits
        "experimental_anti_evasion": True,
        "script_logging": True,
        "input_sample_tampering": True,
        "network_settings": "simulated",
    }

    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(url, files=files, data=data, headers=headers)
            if response.status_code == 201:
                return response.json()
            else:
                with open("err_logs.txt", 'a') as f:
                    f.write(f"{filename} Failed to submit file. Response: {response.json()}\n")
                return None
    except Exception as e:
        with open("err_logs.txt", 'a') as f:
            f.write(f"{filename} Error submitting file: {str(e)}\n")
        return None


def main():

    directory_path = r"C:\Users\dunca\Desktop\b"


    file_list = os.listdir(directory_path)

    load_dotenv()
    api_key = os.environ.get("API_KEY")

    total = len(file_list)
    cnt = 1

    with open("err_logs.txt", 'w+') as file:
        file.truncate(0)

    for filename in file_list:

        print("///////////////////////////// \n")
        print("Working on " + filename)
        print(str(cnt) + "/" + str(total))
        if cnt==101:
            print("Limit !!!")
            break
        cnt+=1


        file_path = os.path.join(directory_path, filename)



        response = submit_file(file_path, api_key,filename)
        if response:
            print("File submitted successfully.")
            analysis_id = response.get("job_id")

            with open("analysis_id.txt", 'w+') as f:
                    f.write(f"{analysis_id}\n")

        else:
            print(f"Failed to submit the file: {response.json()}")

if __name__ == "__main__":
    main()
