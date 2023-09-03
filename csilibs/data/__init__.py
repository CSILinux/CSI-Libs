import sqlite3, json, os

_abs_path = os.path.abspath(os.path.dirname(__file__))  

class Sites_User:
    SITES_SOCIAL = "Social_sites"
    SITES_NSFW = "NSFW_sites"
    SITES_ONION = "Onion_sites"
    SITES_FIN = "Financial_sites"
    SITES_GAMING = "Gaming_sites"

    db_filename = os.path.join(_abs_path,'sites_userenum.db')
    
    @staticmethod
    def get_data(sites_category=SITES_SOCIAL):   
        with sqlite3.connect(Sites_User.db_filename) as conn:
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
    
