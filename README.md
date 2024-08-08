# RansoGuard
## Overview
RansoGuard is a graphical user interface Windows application that given a portable executable, it predicts the ransomware family the sample belongs to and generates a report. Following the file upload, three static tools and one dynamic tool run in parallel and extract the 783 selected features identified as the most valuable (using the [Information Gain Method](https://weka.sourceforge.io/doc.dev/weka/attributeSelection/InfoGainAttributeEval.html) from [WEKA](https://ml.cms.waikato.ac.nz/weka/)). The static tools used are: 
- [floss](https://github.com/mandiant/flare-floss) - for extracting the strings from a file 
- [exiftool](https://exiftool.org/) - for obtaining metadata 
- [pefile](https://github.com/erocarrera/pefile) - a Python library for retrieving PE-specific information.
  
Dynamic analysis is performed using the [Hybrid-Analysis API](https://hybrid-analysis.com/docs/api/v2). The application initiates a request to submit the file for examination in a sandbox environment, then waits for completion before making a final API call to retrieve a summary report. From this report details about network activity, MITRE ATT\&CK techniques present in the program and signatures that indicate specific behavioral characteristics are extracted.

Once both the static and dynamic analysis are completed, a Random Forest machine learning model predicts in what ransomware family does the file belong to based on the extracted features. Finally, a report window is generated and showed to the user.

The application offers a history tab, where users can see a list of their previously analyzed file names and the family prediction. Clicking on an item in the list opens the report window for that file, allowing users to revise the information. Additionally, they can visit the help tab for and explanation of the application's functionality.

The model was trained and tested on 707 samples across 99 families achieved an accuracy of 71.83\%, along with a precision of 0.79 and recall of 0.72.

Below is a screenshot from the app with a report generated for a file a.exe predicted as xoris:

<img src="https://github.com/raul-dunca/assets/blob/main/.images/report.png?raw=true">

<!--A paper about the research done and the application was published: <link>-->

## Installation Guide

1) Clone the repo
```bash
git clone https://github.com/raul-dunca/ransoguard.git
```
2) Navigate to your_path/ransoguard/project
```bash
cd your_path/ransoguard/project
```
3) Make sure you have a Python Version >=3.7 installed. Check using:
```bash
python --version
```
4) Install the required packages
```bash
pip install -r requirements.txt
```
5) Install exiftool from https://exiftool.org/
6) Add exiftool to the PATH environment variable (makes sure the name is exiftool.exe)
7) Install floss from https://github.com/mandiant/flare-floss
8) Add floss to the PATH environment variable (makes sure the name is floss.exe)
9) Create an account on https://hybrid-analysis.com/ and add your API key to the .env file
10) Run the app
```bash
python .\main.py
```

   
