import sys, os, shutil, subprocess, platform, json, random, re
import zipfile, tempfile
from PySide2.QtCore import QDateTime

def pathme(relative_path, set_for_pyinstaller=False):
    """
    Returns the absolute path based on the operating system or the given relative path depends on the availability

    If the script is compiled using PyInstaller, it retrieves the path from the temporary folder created by PyInstaller.
    Otherwise, it checks if the relative path exists in the current directory. If it does, it returns the relative path.
    If the relative path doesn't exist, it creates a better absolute path based on the operating system.

	When you want to include the ICO/image in the executable bundle, provide 'True' as the 2nd argument.
    
    Args:
        relative_path (str): The path relative to the current directory.

    Returns:
        str: The absolute path based on the operating system and the given relative path.

    Raises:
        Exception: If the operating system is not supported.

    """
    if set_for_pyinstaller:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        try:
            base_path = sys._MEIPASS
            relative_path = os.path.basename(relative_path)

            return os.path.join(base_path, relative_path)
        except:
            # not calling from pyinstaller then
            set_for_pyinstaller = False

    if not set_for_pyinstaller:
        
        if os.path.exists(relative_path):
            return relative_path
        
        else:

            os_name = platform.system()
            if os_name == "Windows":
                user_name = os.environ['USERNAME']
                # permissions issues on it
                # architecture = ' (x86)' if platform.architecture()[0] == '32bit' else '' 
                # csitools_dir = f"C:/Program Files{architecture}/csitools"
                csitools_dir = f"C:/Users/{user_name}/AppData/Local/csitools"            

            elif os_name == "Linux":

                csitools_dir = "/opt/csitools" 
                        
            # Please someone implement for mac
            elif os_name == "Darwin":
                pass
            else:
                raise Exception(f"Unsupported operating system: {os_name}")
            

            return os.path.join(csitools_dir,relative_path)
            
        
#---- dynamically generates absolute path for different platforms having different usernames
class CaseDirMe:
    
    """
    A class to dynamically retrieve the case directory.

    Args:
        case_name (str, optional): The name of the specific case directory. Defaults to ''.
        create (bool, optional): Whether to create a new case directory. Defaults to False.
        config_file (str, optional): The path to the configuration file. Defaults to "agency_data.json".

    Attributes:
        case_dir (str): The path to the case directory.
        cases_folder (str): The path to the cases folder.

    Raises:
        Exception: If the operating system is not supported.

    Methods:
        default_cases_dir(): Returns the default case directory location according to the operating system.
    """
    def __init__(self, case_name = '', create=False, config_file="agency_data.json"):        
        # finds the cases_folder location otherwise generate the default ones according to OS
        with open(pathme(f"data/{config_file}"), "r") as file:
            data = json.load(file)
            if data.get("cases_folder") == '':  # by default agency_data.json shouldn't have any folder so that it can generate according to platform
                self.cases_folder = self.defaultCasesDir()
                data["cases_folder"] = self.cases_folder
                with open(pathme("data/agency_data.json"),"w") as json_file:
                    json.dump(data, json_file)
            else:
                self.cases_folder = data.get("cases_folder")

        if case_name != '':
            self.case_dir = os.path.join(self.cases_folder,case_name)
            if not os.path.exists(self.case_dir):
                self.createCase()
        elif create == True:
            if case_name == '':
                self.createCase()
        else:
            self.case_dir = os.path.join(self.cases_folder, case_name)

    # returns default CasesDir location according to OS
    @staticmethod
    def defaultCasesDir():
        os_name = platform.system()
        if os_name == "Windows":
            user_name = os.environ['USERNAME']
            cases_folder = f"C:/Users/{user_name}/Cases"

        elif os_name == "Linux":
            # takes the username if it's not root otherwise takes the user that is in sudo group
            user_name = os.environ['USER'] if os.environ['USER'] != 'root' else subprocess.check_output(['awk', 'BEGIN {FS=":"} {if ($1 == "sudo") print $NF}', '/etc/group']).decode().removesuffix('\n') 
            cases_folder = f"/home/{user_name}/Cases"

        elif os_name == "Darwin":
            pass

        else:
            raise Exception(f"Unsupported operating system: {os_name}")
        
        return cases_folder
    
    def createCase(self):
        from .config import new_case_wizard
        
        try:
            self.case_dir = new_case_wizard()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            sys.exit()



def get_current_timestamp(timestamp=None):
    if timestamp is None:
        timestamp = QDateTime.currentDateTime().toString('yyyy-MM-dd:hh:mm:ss.zzz')
    else:
        timestamp = QDateTime.fromString(timestamp, 'yyyy-MM-dd:hh:mm').toString('yyyy-MM-dd:hh:mm:ss.zzz')
    return f"{timestamp}"

def auditme(case_directory, message):
    audit_log_path = os.path.join(case_directory, "audit.log")
    
    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(case_directory):
        os.makedirs(case_directory)

    # Now it's safe to open the file
    with open(audit_log_path, 'a+') as f:
        f.write(get_current_timestamp() +":\t"+ message + "\n")


def get_random_useragent():
    with open(pathme("data/User_Agents.json"), "r") as file:
        user_agents = json.load(file)
    
    random_header = random.choice(user_agents)
    return {'User-Agent': random_header}
    
    # Feel free to add or modify the browser headers as needed.

def reportme(tmpl_path,out_path,data_dict, img_dict=None):
    """
    fill_template(tmpl_path, out_path, data_dict, img_list):
        Fills in the fields of the template document with data and generates a result document.

    Args:
        tmpl_path (str): Path of the template document that contains the fields to be filled in.
        out_path (str): Path of the resulting document with placeholders replaced by data.
        data_dict (dict): A dictionary mapping placeholder names to their corresponding values for replacement.
        img_list (dict): A dictionary specifying the images to replace in the document. 
            Key: The position of the image, docx and odt have different positions arrangement.
            Value: The path to the image file.

    Note:
    - In ODT files: Position of Images depends on the order of adding them not the format of document.
        - if someone adds the image first but adds it to the last page still it will gonna have 0 position.
    - In DOCX files: Position of Images depends on the format of document.
        - if someone adds the image first but adds it to the last page then it will gonna have last position.

    Example:
        tmpl_path = 'template.odt'
        out_path = 'result.odt'
        data_dict = {'placeholder1': 'value1', 'placeholder2': 'value2'}
        img_list = {0: 'image1.png', 1: 'image2.png'}
        fill_template(tmpl_path, out_path, data_dict, img_list)
    """
    
    if tmpl_path.lower().endswith(".odt"):
       
        # Create a temporary directory to extract the ODT contents
        temp_dir = tempfile.mkdtemp()

        # Extract the ODT contents to the temporary directory
        with zipfile.ZipFile(tmpl_path, 'r') as odt_file:
            odt_file.extractall(temp_dir)

        # Read the styles.xml file for header and footer
        content_path = os.path.join(temp_dir, 'styles.xml')
        with open(content_path, 'r') as content_file:
            content = content_file.read()
            content_file.close()
        
        # regex pattern to find placeholder and replace with the value
        for placeholder, value in data_dict.items(): 
            content = re.sub(rf'<text:user-defined[^&]*?>&lt;{placeholder}&gt;</text:user-defined>', value, content)

        # Write the modified content back to styles.xml
        with open(content_path, 'w') as modified_file:
            modified_file.write(content)
            modified_file.close()

        # Read the content.xml file
        content_path = os.path.join(temp_dir, 'content.xml')
        with open(content_path, 'r', encoding='utf-8') as content_file:
            content = content_file.read()
            content_file.close()

        # regex pattern to find placeholder and replace with the value
        for placeholder, value in data_dict.items():
            # dealing with adding multi line value to the variable in xml using heavy regex
            if '\n' in value:
                values = value.split('\n')

                main_search_string = f'<text:user-defined[^&]*?>&lt;{placeholder}&gt;</text:user-defined>'

                occurrences = re.finditer(rf'({main_search_string})(.*?</text:p>)', content)

                for count, occurrence in enumerate(occurrences):
                    temp = re.search(rf'<.*>', occurrence.group(2))
                    posttext = temp.group()
                    tags = posttext.strip('</>')
                    tags = tags.split('></')
                    
                    re_pretext = ''
                    for i in range(0, len(tags)):
                        tag = tags[len(tags) - i - 1]
                        re_pretext += f'(<{tag}[^>]*>)'
                        if tag == 'text:p':
                            re_pretext += '(?:(?!<text:p).)*?'

                    temp = re.search(rf'{re_pretext}({main_search_string})(.*?</text:p>)', content)

                    pretext = ''
                    for i in range(0, len(tags)):
                        pretext += temp.group(i + 1)

                    data_multiline = ''
                    for i, val in enumerate(values):
                        if i == 0:
                            data_multiline += f"{val}{posttext}"
                        elif i == len(values) - 1:
                            data_multiline += f'{pretext}{val}'
                        else:
                            data_multiline += f'{pretext}{val}{posttext}'
                    content = re.sub(re.escape(occurrence.group(1)), data_multiline, content, count=count+1)

            else:
                content = re.sub(rf'<text:user-defined[^&]*?>&lt;{placeholder}&gt;</text:user-defined>', value, content)

        # replace the placeholder images
        if not img_dict == None:
            file_names = re.findall(r'"Pictures/([^"]+)"', content)
            try:
                for num, imgPath in img_dict.items():
                    shutil.copy(imgPath,os.path.join(temp_dir, f'Pictures/{file_names[len(file_names)-int(num)-1]}'))
            except IndexError:
                print(f'You have only {len(file_names)} image/s in the doc. Index starts from 0')
                
        # Write the modified content back to content.xml
        with open(content_path, 'w') as modified_file:
            modified_file.write(content)
            modified_file.close()
        # Create a new ODT file with the modified content
        with zipfile.ZipFile(out_path, 'w') as modified_odt:
            # Add the modified content.xml back to the ODT
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    modified_odt.write(file_path, arcname)

        # print("Modified file saved as:", out_path)
        # print(temp_dir)
        shutil.rmtree(temp_dir)
    
    if tmpl_path.lower().endswith(".docx"):
        # Create a temporary directory to extract the DOCX contents
        temp_dir = tempfile.mkdtemp()

        # Extract the ODT contents to the temporary directory
        with zipfile.ZipFile(tmpl_path, 'r') as odt_file:
            odt_file.extractall(temp_dir)
        
        content_path = os.path.join(temp_dir, 'word','header1.xml')
        # Read the header.xml and footer.xml file for header and footer
        if  os.path.isfile(content_path):
            # header.xml
            with open(content_path, 'r') as content_file:
                content = content_file.read()
                content_file.close()
            
            # regex pattern to find placeholder and replace with the value
            for placeholder, value in data_dict.items(): 
                content = re.sub(rf'&lt;{placeholder}&gt;', value, content)

            # Write the modified content back to styles.xml
            with open(content_path, 'w') as modified_file:
                modified_file.write(content)
                modified_file.close()

            # footer.xml
            content_path = os.path.join(temp_dir, 'word','footer1.xml')
            with open(content_path, 'r') as content_file:
                content = content_file.read()
                content_file.close()
            
            # regex pattern to find placeholder and replace with the value
            for placeholder, value in data_dict.items(): 
                content = re.sub(rf'&lt;{placeholder}&gt;', value, content)

            # Write the modified content back to styles.xml
            with open(content_path, 'w') as modified_file:
                modified_file.write(content)
                modified_file.close()
        
        # Read the document.xml file
        content_path = os.path.join(temp_dir, 'word', 'document.xml')
        with open(content_path, 'r', encoding='utf-8') as content_file:
            content = content_file.read()
            content_file.close()
        
        # regex pattern to find placeholder and replace with the value
        for placeholder, value in data_dict.items():
            # dealing with adding multi line value to the variable in xml using heavy regex
            # if False:
            if '\n' in value:
                values = value.split('\n')

                main_search_string = f'&lt;{placeholder}&gt;'
                
                occurrences = re.finditer(rf'(<w:p>(?:(?!<w:p>).)*?)(<w:r>(?:(?!<w:r>).)*?)<w:t>[^<>]*?({main_search_string})', content)
                

                for count, occurrence in enumerate(occurrences):    
                    # pretext to add new line
                    # condition to check if placeholder is in bullet point then add new <w:p>
                    if '<w:numPr><w:ilvl w:val="0"/>' in occurrence.group(1):   
                        # This is just like pressing enter in docx
                        # print('list found!')
                        pretext = occurrence.group(1) + occurrence.group(2) + '<w:t>'
                        posttext = '</w:t></w:r></w:p>'
                    # if not bullet point then to keep the consistent style just do <w:br>
                    else:
                        # This is just like pressing shift + enter in docx
                        pretext = occurrence.group(2) + '<w:br w:type="textWrapping"/></w:r>' + occurrence.group(2) + '<w:t>'
                        posttext = '</w:t></w:r>'
                        

                    data_multiline = ''
                    for i, val in enumerate(values):
                        if i == 0:
                            data_multiline += f"{val}{posttext}"
                        elif i == len(values) - 1:
                            data_multiline += f'{pretext}{val}'
                        else:
                            data_multiline += f'{pretext}{val}{posttext}'

                    content = re.sub(re.escape(occurrence.group(3)), data_multiline, content, count=count+1)

            else:
                content = re.sub(rf'&lt;{placeholder}&gt;', value, content)

        # replace the placeholder images
        if not img_dict == None:
            img_dir = os.path.join(temp_dir,'word','media')
            file_names = os.listdir(img_dir)
            try:
                for num, imgPath in img_dict.items():
                    shutil.copy(imgPath,os.path.join(img_dir, f'{file_names[int(num)]}'))
                    print
            except IndexError:
                print(f'You have only {len(file_names)} image/s in the doc. Index starts from 0')
                
        # Write the modified content back to content.xml
        with open(content_path, 'w') as modified_file:
            modified_file.write(content)
            modified_file.close()
        # Create a new ODT file with the modified content
        with zipfile.ZipFile(out_path, 'w') as modified_odt:
            # Add the modified content.xml back to the ODT
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    modified_odt.write(file_path, arcname)

        # print("Modified file saved as:", out_path)
        # print(temp_dir)
        shutil.rmtree(temp_dir)
