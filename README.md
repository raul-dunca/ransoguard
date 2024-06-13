# RansoGuard
## Overview
RansoGuard is a graphical user interface Windows application that given a file, it predicts the ransomware family the sample belongs to and generates a report. Users can upload one file at a time. The file must be a portable executable, since the tools used to extract its features have this requirement. Following the upload, three static tools and one dynamic tool run in parallel and extract the 783 selected features identified as the most valuable. The static tools used are: 
- [floss](https://github.com/mandiant/flare-floss) - for extracting the strings from a file 
- [exiftool](https://exiftool.org/) - for obtaining metadata 
- [pefile](https://github.com/erocarrera/pefile) - a Python library for retrieving PE-specific information.
  
Dynamic analysis is performed using the [Hybrid-Analysis API](https://hybrid-analysis.com/docs/api/v2). The application initiates a request to submit the file for examination in a sandbox environment, then waits for completion before making a final API call to retrieve a summary report. From this report details about network activity, MITRE ATT\&CK techniques present in the program and signatures that indicate specific behavioral characteristics are extracted.

Once both the static and dynamic analysis are completed, a Random Forest machine learning model predicts in what ransomware family does the file belong to based on the extracted features. Finally, a report window appears on the user's screen, allowing them to upload a file again, while at the same time having the option to review a generated report containing the model's prediction and the 783 features with the extracted values.

The application offers a history tab, where users can see a list of their previously analyzed file names and the family prediction. Clicking on an item in the list opens the report window for that file, allowing users to revise the information. Additionally, they can visit the help tab for and explanation of the application's functionality.

The model was trained and tested on 707 samples across 99 families achieved an accuracy of 71.83\%, along with a precision of 0.79 and recall of 0.72.

## Installation Guide

1) Clone the repo
```bash
git clone https://github.com/raul-dunca/ransoguard.git
```
2) Navigate to your_path/ransoguard/project
```bash
cd your_path/ransoguard/project
```
3) Install the required packages
```bash
pip install -r requirements.txt
```
3) Install exiftool from https://exiftool.org/
4) Add exiftool to the PATH environment variable (makes sure the name is exiftool.exe)
5) Install floss from https://github.com/mandiant/flare-floss
6) Add floss to the PATH environment variable (makes sure the name is floss.exe)
7) Create an account on https://hybrid-analysis.com/ and add your API key to the .env file
8) Run the app
```bash
python .\main.py
```

   
