import queue
import re
import subprocess
import threading
from collections import Counter

import pefile
from PyQt5.QtCore import QMutex

error_mtx=QMutex()
dict_mutex=QMutex()
error_queue=queue.Queue()
features_dictionary={}
def run_exiftool(file_path):
     """
     executes exiftool on the file_path and error handles it
     """
     command = "exiftool " + file_path

     result=subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

     if result.stderr:
         error_message = f"Exiftool Error: {result.stderr.decode('utf-8')}"
         error_mtx.lock()
         error_queue.put(error_message)
         error_mtx.unlock()
     else:
        output = result.stdout.decode('utf-8')
        for line in output.strip().split('\n'):
            key,value = line.split(':',1)
            if key.strip()=="Directory":
                continue
            elif key.strip()=="File Name":
                continue
            elif key.strip()=="ExifTool Version Number":
                continue

            dict_mutex.lock()

            if key.strip() in features_dictionary:
                print(key)


            features_dictionary[key.strip()]=value.strip()
            dict_mutex.unlock()

def run_floss(file_path):
        """
        executes floss on the file_path and error handles it
        """

        command = "floss -L -q " + file_path

        result=subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode !=0:
            error_message = f"Floss Error: failed to analyze sample"
            error_mtx.lock()
            error_queue.put(error_message)
            error_mtx.unlock()
        else:
            output = result.stdout.decode('utf-8')

            dict_mutex.lock()
            lines = ["str_"+line.strip() for line in output.split('\n') if line.strip() not in features_dictionary]
            string_counter = Counter(lines)
            features_dictionary.update(string_counter)
            dict_mutex.unlock()

def run_dependency(file_path):
        """
        executes Dependencies on the file_path and error handles it
        """

        command = "Dependencies -modules " + file_path
        #with open("output_dep", 'w+') as f:
        result=subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.stderr:
            error_message = f"Dependencies Error: {result.stderr.decode('utf-8')}"
            error_mtx.lock()
            error_queue.put(error_message)
            error_mtx.unlock()
        else:
            output = result.stdout.decode('utf-8')
            lines = output.strip().split('\n')
            for i in range(1,len(lines)):
                line=lines[i]
                parts = line.split('] ')
                if len(parts) > 1:
                    dll_info = parts[1].split(' : ')
                    if len(dll_info)==2:
                        dll=dll_info[0].strip()
                        dict_mutex.lock()
                        if dll in features_dictionary:
                            print(dll)
                        features_dictionary[dll] = 1
                        dict_mutex.unlock()
                    elif len(dll_info)==1:
                        dll=dll_info[0][:-1].strip()
                        dict_mutex.lock()
                        if dll in features_dictionary:
                            print(dll)
                        features_dictionary[dll] = 1
                        dict_mutex.unlock()
                    else:
                        print("WHAT happened??????? Dependency error??")

def hex_to_int(hex_string):
    # Remove the '0x' prefix
    hex_string = hex_string[2:]

    # If it's a single byte, convert directly to integer
    if len(hex_string) <= 2:
        return int(hex_string, 16)

    # Otherwise, pad the hexadecimal string with zeros to ensure it's an even number of digits
    hex_string = hex_string.rjust((len(hex_string) + 1) // 2 * 2, '0')
    little_endian_bytes = bytes.fromhex(hex_string)[::-1]
    return int.from_bytes(little_endian_bytes, byteorder='big')


def run_pefile(file_path):
        """
        executes pefile on the file_path
        """
        file_path=file_path.strip('"')          #necessary bcs file_path is quoted (in case it has space) byt pefile takes care of that case already
        try:
            pe = pefile.PE(file_path)
            output=str(pe)


            hex_pattern = r"0[xX][0-9A-Fa-f]+"
            ignore_start = "Unwind data for exception handling"
            title=""

            index=0
            imported_symbols=[]
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                imported_symbols.append(entry.dll.decode())         #create a imported symbols list


            for line in output.strip().split('\n'):

                if ignore_start in line:
                    break

                if line.startswith("[") and line.endswith("]"):
                    title=line[1:-1]

                if title=="IMAGE_IMPORT_DESCRIPTOR":            #we are in the Imported Symbols section
                    title=imported_symbols[index]
                    index+=1

                if title!="" and  line.startswith(title):       #add dll functions imported to the feature_dictionary
                    dll=line.split()[0]
                    dict_mutex.lock()
                    if dll in features_dictionary:
                        print(dll)
                    features_dictionary[dll] = 1
                    dict_mutex.unlock()

                match = re.findall(hex_pattern, line)
                if match:
                    if len(match)>=3:
                        field_name, value = line.split()[2], match[2]
                        #value = int(value, 16)  or   value = hex_to_int(value)
                    else:
                        field_name, value = line.split()[2], 0

                    if field_name == "Name:" and title == "IMAGE_SECTION_HEADER":  # we are inside the PE Sections section
                        title = line.split(':')[1].strip()
                    else:
                        field_name=field_name[:-1]
                        dict_mutex.lock()
                        if field_name in features_dictionary:
                            print(field_name)
                        features_dictionary[title+"_"+field_name] = value
                        dict_mutex.unlock()

        except Exception as e:
            error_message = f"Pefile Error: {e.args[0]}"
            error_mtx.lock()
            error_queue.put(error_message)
            error_mtx.unlock()


def perform_static_analysis():
    thread_pefile = threading.Thread(target=run_pefile, args=(quoted_file_path,))
    thread_floss = threading.Thread(target=run_floss, args=(quoted_file_path,))
    thread_dependency = threading.Thread(target=run_dependency, args=(quoted_file_path,))
    thread_exiftool = threading.Thread(target=run_exiftool, args=(quoted_file_path,))

    thread_pefile.start()
    thread_floss.start()
    thread_dependency.start()
    thread_exiftool.start()

    thread_pefile.join()
    thread_floss.join()
    thread_dependency.join()
    thread_exiftool.join()

file_path= r"C:\Users\dunca\Desktop\a.exe"
#file_path=r"C:\MatLab install\bin\matlab.exe"

quoted_file_path = '"{}"'.format(file_path)



perform_static_analysis()


error_message=""
while not error_queue.empty():
    error_message += error_queue.get().strip() + '\n'
print(error_message)


with open("output.txt", 'w+', encoding='utf-8') as file:
    # Iterate over the dictionary and write each key-value pair to the file
    for key, value in features_dictionary.items():
        file.write(f"{key}: {value}\n")



