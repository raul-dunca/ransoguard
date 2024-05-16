import csv
import os

import requests
import time



from dotenv import load_dotenv




def get_analysis_report(api_key, analysis_id,filename, features_dir):
    url = f"https://www.hybrid-analysis.com/api/v2/report/{analysis_id}/summary"
    headers = {
        "User-Agent": "Falcon Sandbox",
        "api-key": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            """
            SIGNATURES are:
            The features provided in the JSON snippet are indicators of potentially malicious behavior exhibited by a file or program. Each "signature" contains information about a specific behavior or capability observed during the dynamic analysis. Here's a breakdown of the details provided:

threat_level: Indicates the perceived threat level of the behavior.
threat_level_human: A human-readable version of the threat level.
category: The general category of the behavior.
identifier: An identifier for the specific behavior.
type: Type of behavior or indicator.
relevance: The relevance of the behavior.
name: Name or description of the behavior.
description: Detailed description of the behavior or indicator.
origin: The source of the behavior (e.g., file or memory).
attck_id: ATT&CK technique ID associated with the behavior (if applicable).
capec_id: CAPEC ID associated with the behavior (if applicable).
attck_id_wiki: Link to more information about the ATT&CK technique on the MITRE ATT&CK framework.
            """



            json_resp=response.json()
            if json_resp["av_detect"]:
                features_dir["av_detect"]=json_resp["av_detect"]
            if json_resp["threat_score"]:
                features_dir["threat_score"] = json_resp["threat_score"]
            if json_resp["threat_level"]:
                features_dir["threat_level"]=json_resp["threat_level"]

            for domain in json_resp["domains"]:
                features_dir[domain]=1

            for host in json_resp["hosts"]:
                features_dir[host] = 1

            for comp_host in json_resp["compromised_hosts"]:
                features_dir["Comp": comp_host] = 1

            if json_resp["total_network_connections"]:
                features_dir["total_network_connections"]=json_resp["total_network_connections"]
            if json_resp["total_processes"]:
                features_dir["total_processes"]=json_resp["total_processes"]
            if json_resp["total_signatures"]:
                features_dir["total_signatures"]=json_resp["total_signatures"]

            for extracted_file in json_resp["extracted_files"]:
                if extracted_file["name"]:
                    features_dir["EXTR_"+extracted_file["name"]]=1
                    if extracted_file["file_size"]:
                        features_dir["EXTR_"+extracted_file["name"]+"_SIZE"] = extracted_file["file_size"]
                    if extracted_file["threat_level"]:
                        features_dir["EXTR_" + extracted_file["name"] + "_THRD_LVL"] = extracted_file["threat_level"]
                    if extracted_file["av_matched"]:
                        features_dir["EXTR_" + extracted_file["name"] + "_AV_MATCH"] = extracted_file["av_matched"]
                    if extracted_file["av_total"]:
                        features_dir["EXTR_" + extracted_file["name"] + "_AV_T"] = extracted_file["av_total"]

            for processes in json_resp["processes"]:
                if processes["name"]:
                    features_dir["PROC_"+processes["name"]]=1
                    if processes["av_matched"]:
                        features_dir["PROC_" + processes["name"] +"_AV_MATCH"] = processes["av_matched"]
                    if processes["av_total"]:
                        features_dir["PROC_" + processes["name"] + "_AV_T"] = processes["av_total"]

                    if len(processes["file_accesses"])>0:
                        if "FILE_ACCESSESD" not in features_dir:
                            features_dir["FILE_ACCESSESD"]=len(processes["file_accesses"])
                        else:
                            features_dir["FILE_ACCESSESD"]+=len(processes["file_accesses"])

                    if len(processes["created_files"]) > 0:
                        if "FILE_CREATED" not in features_dir:
                            features_dir["FILE_CREATED"] = len(processes["created_files"])
                        else:
                            features_dir["FILE_CREATED"] += len(processes["created_files"])
            for attack in json_resp["mitre_attcks"]:
                if attack["tactic"]:
                   features_dir[attack["tactic"]]=1
                if attack["technique"]:
                   features_dir[attack["technique"]]=1
                if attack["attck_id"]:
                   features_dir[attack["attck_id"]]=1

            for signature in json_resp["signatures"]:
                if signature["name"]:
                    features_dir["SIG_"+signature["name"]] = 1
                    if signature["relevance"]:
                        features_dir["SIG_" + signature["name"]+"_REL"] = signature["relevance"]
                    if signature["threat_level"]:
                        features_dir["SIG_" + signature["name"]+"_THRD_LVL"] = signature["threat_level"]

            return True
        else:
            with open("err_logs.txt", 'a') as f:
                f.write(f"{filename} Failed to get analysis report. Response: {response.json()}")
            return None
    except Exception as e:
        with open("err_logs.txt", 'a') as f:
            f.write(f"{filename} Error getting analysis report: {str(e)}")
        return None


def write_dicts_to_csv(file_path, dictionary):

    fieldnames = dictionary.keys()

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow(dictionary)

def main():

    directory_path = r"C:\Users\dunca\Desktop\b"
    output_dir = r"C:\Users\dunca\Desktop\output_dyn"

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

        output_file_path = os.path.join(output_dir, filename + "_dyn_output.csv")

        features_dictionary = {}


        with open('analysis_id.txt', 'r') as file:
            for id in file:
                get_analysis_report(api_key, id,filename,features_dictionary)
                write_dicts_to_csv(output_file_path, features_dictionary)

if __name__ == "__main__":
    main()
