# Under Development

Currently, @pakcyberbot is assigned to this project. If you have any queries or would like to contribute, please feel free to contact me.

### Purpose
The purpose of this project is to facilitate the development of CSI tools. It includes all the necessary code blocks, as well as assets such as PNG images and data files. Everything is categorized into separate modules.

# If anyone is free work on README file.

## USAGE
#### To use assets
All the necessary images, icons and ui elements are included inside the package.

```python
from csilibs.assets import images, icons

# path of an image.
print(images.CSILINUX_BLACK)    
# path of an icon.
print(icons.CSI_ONION_TOR)      
```

#### To get input from data files
This currently includes agency_data.json, API_Keys.json, sites_userenum.db(urls for getting users in websites).
```python
from csilibs.data import SitesUser, apiKeys, agencyData


print(SitesUser.get_data(SitesUser.SITES_SOCIAL))

print(apiKeys.get_dict())
apiKeys['newWeb_api'] = {'key':'<SECRET>','inTools':['Recon-NG','OSINT-Search']}

print(agencyData.get_dict())
print(agencyData['agency_name'])
```
#### utils module
```python
from csilibs.utils import pathme, CaseDirMe, get_current_timestamp, auditme, get_random_useragent, reportme


```

#### config module
```python
from csilibs.config import agency_wizard, new_case_wizard, gen_case_structure, create_case_folder

```

#### case module
```python
from csilibs.case import closeCase, archiveCase, arcIntegrityCheck, importCase

```

#### networking module
```python

```

#### gui module
```python

```

#### auth module
```python

```

#### constants module
```python

```
