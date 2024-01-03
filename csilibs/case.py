import sys, os, platform, json, subprocess, re 
import time, tempfile, zipfile, shutil

from .auth import gen_md5
from .config import gen_case_structure
from .utils import auditme, CaseDirMe

def closeCase(case):
    """
    Creates a zip file of the specified case folder, including all subfolders containing files.
Additionally, it generates an MD5 hash for each file and stores them in a file named "<zip_file_name>.md5 and archived in the zip file too".
    Naming format
    zip_file_name = <case_name>-<YYYYmmdd>-<HHMM>
    
    Args:
	case_folder (str): The path to the case folder that needs to be zipped.
	    
    Returns:
	None
    """
    # To cope with the problem if path is given by mistake
    if os.path.exists(case) or '/' in case or '\\' in case:
        raise Exception("Input must be a CaseName not any path")

    # Create a temporary directory to store md5 hashes file
    temp_dir = tempfile.mkdtemp()
    case_dir_path = CaseDirMe(case).case_dir

    file_time = time.strftime("%Y%m%d-%H%M")    #time format: YYYYmmdd-HHMM

    md5_temp_path = os.path.join(temp_dir,f"{case}-{file_time}.md5")
    archive_path = os.path.join(CaseDirMe().cases_folder,'Archive',f"{case}-{file_time}.zip")

    # generating hash of every directory
    with open(md5_temp_path,'w') as hash_file:
        for root, dirs, files in os.walk(case_dir_path):
            for f in files:
                file_path = os.path.join(root,f)
                hash_file.write(f"{gen_md5(file_path)} {file_path.replace(case_dir_path,'.')}\n")
        hash_file.close()

    # creates zip file of case folder
    with zipfile.ZipFile(archive_path, 'w') as case_zip:
        for root, _, files in os.walk(case_dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, case_dir_path)
                case_zip.write(file_path, arcname)
        # storing md5 file in zip too
        arcname = os.path.relpath(md5_temp_path, temp_dir)
        case_zip.write(md5_temp_path,arcname)
        case_zip.close()

    shutil.rmtree(temp_dir)
    

def archiveCase(case):
    """
    it calls closeCase() and then removes the case folder 
    
    args: casename to archive and then delete its folder
    """
    closeCase(case)
    case_dir_path = CaseDirMe(case).case_dir
    shutil.rmtree(case_dir_path)
	
def arcIntegrityCheck(archive_path):
    """
    checks the integrity of the given archive file with the absolute path by comparing it with the md5 file located inside the zip archive
    
    args: archive path
    return: tuple ( archive_name , md5_name , list [ altered_files ] )
    """
    # Create a temporary directory to have integrity checks.
    temp_dir = tempfile.mkdtemp()

    # Extract the ODT contents to the temporary directory
    with zipfile.ZipFile(archive_path, 'r') as arc_file:
        arc_file.extractall(temp_dir)
    
    #extracting only name from zip to have md5 file name
    archive_file, _ = os.path.splitext(os.path.basename(archive_path))
    
    #getting md5 file name
    for f in os.listdir(temp_dir):
        if re.search(r'.*\.md5$',f):
            md5_file = f
            print(md5_file)
            break
    
    md5_hash_path = os.path.join(temp_dir, md5_file)

    altered_files = []
    with open(md5_hash_path,'r') as hash_file:
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f != md5_file:  # present in the same directory
                    file_path = os.path.join(root,f)
                    md5hash = hash_file.readline()
                    if md5hash.startswith(gen_md5(file_path)):
                        print(f"{f} file hash verified!")
                    else:
                        print(f"{f} file failed the integrity check")
                        altered_files.append(os.path.relpath(os.path.join(root,f),temp_dir))    # relative path to the file with respect to zip
    
    shutil.rmtree(temp_dir)
    return (archive_file, md5_file, altered_files)

def importCase(archive_path):
    """
    Creates a case folder by importing the archive content, if case folder exists then creates with the prefix number to avoid overriding the current case folder
    
    args: archive_path 
    """
    arc_name, md5_name, altered_files = arcIntegrityCheck(archive_path)
    
    casename = md5_name.split('-')[0]

    case_dir_path = CaseDirMe(casename).case_dir
    
    # Create a temporary directory to extract only approved file in the case folder.
    temp_dir = tempfile.mkdtemp()
    
    with zipfile.ZipFile(archive_path, 'r') as arc_file:
        arc_file.extractall(temp_dir)

    # to add numbering if there are multiple cases in the folder to avoid overiding the case folder
    count = 0
    temp = case_dir_path
    while os.path.isdir(case_dir_path if count == 0 else f"{case_dir_path}-{count}"):
        count +=1
    
    case_dir_path = case_dir_path if count == 0 else f"{case_dir_path}-{count}"

    with zipfile.ZipFile(archive_path, 'r') as arc_file:
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f != md5_name:  # not extracts the md5 file.
                    file_path_in_zip = os.path.relpath(os.path.join(root,f),temp_dir)
                    if not file_path_in_zip in altered_files:
                        arc_file.extract(file_path_in_zip, case_dir_path)
    
    for alt_file in altered_files:
        auditme(case_dir_path, f"{alt_file} file FAILED the integrity check!")
    
    gen_case_structure(case_dir_path)
    
    shutil.rmtree(temp_dir)
    