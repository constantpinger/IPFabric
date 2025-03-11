################
#
# Retreives all attributes from the latest IP Fabric snapshot
# Checks if any comply with logic of being of type siteName, 6 characters long and have lowercase chars
# Checks if the serial number of the filtered list has another attribute with name MRS and value y
# If not then updates the value of attribute with uppercase
#
# This logic assumes that all site names except for MRS should be uppercase and 6 chars long
#
################

from ipfabric import IPFClient
from ipfabric.settings import Attributes
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

snapshot_id='$last'  # replace with specific snapshot ID if required
TOKEN = "4932f6abf6b0184e9b042b49dbf6f595"
payload = {"snapshot": snapshot_id,  "columns": [ "sn",    "hostname",    "name",    "value"  ],}  # The IPF specific params
headers = {'Content-Type': 'application/json', 'X-API-Token': TOKEN}

#Searches the provided list of dictionaries for matches against the serial number sn, then returns True only if there is not an entry stating MRS = n
def CheckNotMRS(sn, search_list):
    # Search search_list for all elements that match sn
    ALL_ATTS_FOR_SN = [element for element in search_list if element['sn'] == sn]
    # Within the result search for elements where MRS=n
    FindNonMRSAttribute =  [element for element in ALL_ATTS_FOR_SN if element['name'] == 'MRS' and element['value'] == 'n']
    if len(FindNonMRSAttribute) > 0:  # if there is an attribute then sn is not MRS
        return False
    else:
        return True

# Initiate SDK
ipf = IPFClient(base_url='https://daisy.ja.net/', auth='4932f6abf6b0184e9b042b49dbf6f595', verify=False, timeout=15)

# Supress only InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Get all attributes from the local snapshot
GET_ALL = requests.post('https://daisy.ja.net/api/v7.0/tables/snapshot-attributes',  headers=headers , json = payload, verify=False)

# Result is a dictionary containing a single entry with key=data - This is a list of dicts - Extract the json version and unpack to leave the list
#  {'data': [{'sn': 'CZ5216AF1259', 'hostname': 'rau-ej', 'name': 'JanetRegion', 'value': 'SWR'},
GET_ALL = GET_ALL.json()['data'] #extract the single list item to make the variable
print("Number of Attribtues received: " + str(len(GET_ALL)) + "\n")

# Reset flag to capture if any changes are made during the main section
SomethingChangedFlag = False

for i in GET_ALL:
    # if entry is a siteName and any lowercase chars in the value and 6 digits in length - in IPF use regex:    =~^\b[a-z0-9]{7}\b$
    if (i['name'] == 'siteName') and (any(c.islower() for c in i['value'])) and len(i['value'])==6 :
        print(" ")
        MRSCHECK = CheckNotMRS(i['sn'],GET_ALL)   # Returns False if there is an attribute with mrs=n
        if MRSCHECK:  # if MRS then skip
            print("Skipping sn: " + str(i['sn']) + " because is MRS")
            continue
        else:
            sites = [{'sn': i['sn'], 'value': i['value'].upper()}]    #build a list with a single dict
            print("Changing the siteName of " + str(i['sn']) + " with siteName " + str(i['value']))
            print("New Attribute:      " + str(sites))
            resp = ipf.settings.global_attributes.set_sites_by_sn( sites)   # set global attributes based on sites
            SomethingChangedFlag = True   # set flag so the final step recalculates the snapshot's values and recalculates making the change live

if SomethingChangedFlag:  # Tell IPF to set the snapshot's values to the newly set global values then invoke recalculation so that sites are shown
    ipf_attr = Attributes(client=ipf, snapshot_id=snapshot_id)
    resp = ipf_attr.update_local_attr_from_global()


