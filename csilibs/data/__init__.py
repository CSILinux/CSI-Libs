import sqlite3, json, os, copy

_abs_path = os.path.abspath(os.path.dirname(__file__))  

class SitesUser:
    SITES_SOCIAL = "Social_sites"
    SITES_NSFW = "NSFW_sites"
    SITES_ONION = "Onion_sites"
    SITES_FIN = "Financial_sites"
    SITES_GAMING = "Gaming_sites"

    db_filename = os.path.join(_abs_path,'sites_userenum.db')
    
    @staticmethod
    def get_data(sites_category=SITES_SOCIAL):   
        with sqlite3.connect(SitesUser.db_filename) as conn:
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {sites_category}")
            rows = cursor.fetchall()
            
            def row_to_dict(row, cursor):
                return {
                    cursor.description[i][0]: value for i, value in enumerate(row)
                }

            # Convert the rows to dictionaries
            result = [row_to_dict(row, cursor) for row in rows]
            return result
    # Later implement write functionality too
    

class __JsonData:
    def __init__(self, filename):
        self.file_path = os.path.join(_abs_path,filename)
        try:
            with open(self.file_path, 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            return None
    
    def get_dict(self):
        return self.data

    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.data, file, indent=4)
            return True
        except Exception as e:
            return False
        
    
    def set_dict(self, data):
        self.data = data
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.data, file, indent=4)
            return True
        except Exception as e:
            return False
        
    def __str__(self) -> str:
        return repr(self.data)

    
agencyData = __JsonData('agency_data.json')
apiKeys = __JsonData('APIKeys.json')
