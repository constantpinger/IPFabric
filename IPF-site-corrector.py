###  sets the siteName value for any attribtue that is not for a device with custom attribtue MRS set to y

from ipfabric import IPFClient
from ipfabric.settings import Attributes
import requests

switch="global"
TOKEN = "4932f6abf6b0184e9b042b49dbf6f595"
snapshot_id='$last'
#snapshot_id='9f3bd47a-f2d4-4936-95db-0a65843f4701'

ipf = IPFClient(base_url='https://daisy.ja.net/', auth='4932f6abf6b0184e9b042b49dbf6f595', verify=False, timeout=15)

session = requests.Session()
session.headers.update({'Content-Type': 'application/json', 'X-API-Token': TOKEN})

payload = {"snapshot": snapshot_id,  "columns": [ "sn",    "hostname",    "name",    "value"  ],}
GET_ALL = session.post('https://daisy.ja.net/api/v7.0/tables/snapshot-attributes', json=payload, verify=False)
GET_ALL = GET_ALL.json()['data']

def CheckNotMRS(sn, search_list):
    ALL_ATTS_FOR_SN = [element for element in search_list if element['sn'] == sn]
    return [element for element in ALL_ATTS_FOR_SN if element['name'] == 'MRS' and element['value'] == 'n']

SomethingChangedFlag = False
for i in GET_ALL:
    #  {'sn': 'F0069', 'name': 'siteName', 'value': 'NOCFLB'}
    if (i['name'] == 'siteName') and (any(c.islower() for c in i['value'])) and len(i['value'])==6 :    # if entry is a siteName and any lowercase chars in the value
        print(" ")
        MRSCHECK = CheckNotMRS(i['sn'],GET_ALL)   # returns a list with a single dictionary if MRS value is y
        if len(MRSCHECK) > 0:  # if MRS then take skip
            print("Skipping sn: " + str(i['sn']) + " because is MRS")
            continue
        else:
            print("Changing the siteName of " + str(i['sn']) + " with siteName " + str(i['value']))
            sites = [{'sn': i['sn'], 'value': i['value'].upper()}]    #build a list with a single dict
            resp = ipf.settings.global_attributes.set_sites_by_sn( sites)   # set global attributes based on sites
            print(resp)
            SomethingChangedFlag = True   # set flag so the final step recalculates the snapshot's values and recalculates making the change live
if SomethingChangedFlag:  # Tell IPF to set the snapshot's values to the newly set global values then invoke recalculation so that sites are shown
    ipf_attr = Attributes(client=ipf, snapshot_id=snapshot_id)
    resp = ipf_attr.update_local_attr_from_global()

