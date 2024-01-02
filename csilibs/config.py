import sys, os, platform, json, subprocess
from .utils import auditme, get_current_timestamp, pathme

__abs_path = os.path.abspath(os.path.dirname(__file__))  

def agency_wizard():
    try:
        subprocess.run(["python", os.path.join(__abs_path,"Agency_Wizard.py")])
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit()

def new_case_wizard():
    # returns case_name
    try:
        completed_process = subprocess.run(["python", os.path.join(__abs_path, "New_Case_Wizard.py")], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if completed_process.returncode == 0 and completed_process.stdout != '':
            return os.path.basename(completed_process.stdout.strip())
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
    
# with open(pathme("data/agency_data.json"), "r") as file:
#     data = json.load(file)
#     if data.get("cases_folder") == '':  # by default agency_data.json shouldn't have any folder so that it can generate according to platform
#         cases_folder = casedirMe()
#         data["cases_folder"] = cases_folder
#         with open(pathme("data/agency_data.json"),"w") as json_file:
#             json.dump(data, json_file)
#     else:
#         cases_folder = data.get("cases_folder")

#--- Delete the above commented agency text if 



def gen_case_structure(case_directory):
    
    with open(os.path.join(__abs_path,"data/Case_Structure.json"), "r") as file:
        case_folder_structure = json.load(file)
    for subdirectory in case_folder_structure:
        directory_path = os.path.join(case_directory, subdirectory)
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
    
    auditme(case_directory,"Generating Case Folder Structure")

def create_case_folder(case_directory):
    timestamp = get_current_timestamp()
    if not os.path.exists(case_directory):
        os.makedirs(case_directory)

    gen_case_structure(case_directory)

    audit_log_path = os.path.join(case_directory, "audit.log")
    if not os.path.isfile(audit_log_path):
        with open(audit_log_path, 'a+') as f:
            f.write(get_current_timestamp() + " Audit log created.\n")
    
    history_file_path = os.path.join(case_directory, "history.txt")
    if not os.path.isfile(history_file_path):
        with open(history_file_path, 'a+') as f:
            f.write(get_current_timestamp() + " History file created.\n")
    
    notes_file_path = os.path.join(case_directory, "notes.txt")
    if not os.path.isfile(notes_file_path):
        with open(notes_file_path, 'a+') as f:
            f.write("Case notes for Digital Forensics Investigation:\n" + get_current_timestamp() + "\n\n")
        
    return case_directory
    
