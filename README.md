# RansoGuard
RansoGuard is a graphical user interface Windows application through which users can upload one file at a time. The file must be a portable executable, since the tools used to extract its features have this requirement. Following the upload, three static tools and one dynamic tool run in parallel and extract the 783 selected features identified as the most valuable. The static tools used are: Floss for extracting the strings from a file, Exiftool for obtaining metadata and the pefile Python library for retrieving PE-specific information. Dynamic analysis is performed using the Hybrid-Analysis API. The application initiates a request to submit the file for examination in a sandbox environment, then waits for completion before making a final API call to retrieve a summary report. From this report details about network activity, MITRE ATT\&CK techniques present in the program and signatures that indicate specific behavioral characteristics are extracted. Once both the static and dynamic analysis are completed, the Random Forest machine learning model predicts in what ransomware family does the file belong to based on the extracted features.

Finally, a report window appears on the user's screen, allowing them to upload a file again, while at the same time having the option to review a generated report containing the model's prediction and the 783 features with the extracted values. The application offers a history tab, where users can see a list of their previously analyzed file names and the family prediction. Clicking on an item in the list opens the report window for that file, allowing users to revise the information. Additionally, they can visit the help tab for and explanation of the application's functionality.

The model achieved an accuracy of 71.83\%, along with a precision of 0.79 and recall of 0.72.

## Install
1) pip install -r requirements.txt
2) install [exiftool](https://exiftool.org/install.html) and add the path to the exe to the PATH env variable
3) install [floss](https://github.com/mandiant/flare-floss/tree/7b3a7cd2204bd5de62ca210d0100fbe89ebc0e38) and add the path to the exe to the PATH env variable
4) install [Dependencies](https://github.com/lucasg/Dependencies) and add the path to the exe to the PATH env variable



   ```bash
   pip install -r requirements.txt
