######################################
## Fetch device data from the latest snapshot in IP Fabric
## Fetch live vulnerability information matching the vendor+family+version
## Compile CSV files with findings
######################################

#import json  # only needed if creating the curl commands below for debugging
import nvdlib
from ipfabric import IPFClient
import csv


####  IP FABRIC FETCH   ####

## Define the filters and columns to retrieve from IPF
#filters = {"and": [{ "vendor": ["eq", "cisco"] },{ "family": ["eq", "ios"] }, { "siteName": ["eq", "OAR-OMR"] }          ]}
#filters = {"and": [{ "hostname": ["eq", "yorktd-omr1"]} ]}
filters = {"and": [{ "siteName": ["eq", "WMR"] }  ]}
columns = ["hostname", "vendor", "family", "version", "siteName", "sn", "uptime"]

ipf = IPFClient(base_url='https://<servername>/', auth='<IPF Key>', verify=False, timeout=15)
devices = ipf.inventory.devices.all(filters=filters, columns=columns)
#devices = ipf.inventory.devices.all()    #no filtering and retrieve all columns
print(" ")
print("Total Devices retrieved from IPF is: " + str(len(devices)))

"""   EXAMPLE IPF output
'JN1ASDFAS66'
'mx480'
{'address': ('10.6.0.25',),
 'dev_type': 'router',
 'family': 'junos',
 'fqdn': 'EXAMPLEROUTER.ABC.COM',
 'hostname': 'EXAMPLEROUTER',
 'image': None,
 'ipf_platform': 'mx',
 'ipf_serial': 'JN1ASDFAS66',
 'model': 'mx480',
 'protocol': 'ssh',
 'serial': 'JN1ASDFAS66',
 'site': 'HUB',
 'site_name': 'HUB',
 'sn': 'JN1ASDFAS66',
 'sn_hw': 'JN1ASDFAS66',
 'vendor': 'juniper',
 'version': '16.2R2.8'}
"""




####   Vuln fetch   ####

vulnlist=[]
HighScoreVulnList=[]
nvd_api_key = '<NVD key>'  # can be removed from the vuln retrieval string and it just adds a 6s delay to each search
for item in devices:    # for each device retrieved from IPF
    vendor = item['vendor']
    family = item['family']
    version = item['version'].partition("(")[0]   #use only the part of the string up until the bracket that exists in ios version number as non digits break URL strings
    ## TEST URL for use with curl
    ## url = 'https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName=cpe:2.3:o:' + vendor + ':' + family + ':' + version + ':*:*:*:*:*:*:*'
    cpeMatchString2 = 'cpe:2.3:o:' + vendor + ':' + family + ':' + version + ':*:*:*:*:*:*:*'
    r = nvdlib.searchCVE(cpeName = cpeMatchString2, key=nvd_api_key , delay=1)    # retrieve the vulnerabilities for the device+OS
    if len(r) < 1:   #if no vulnerabilities found for the search criteria
        vulnlist.append([item['hostname'],item['vendor'],item['family'],item['version'],"NO CVE",""  ])
        continue
    for eachCVE in r:   #extract the data and place as a row in the list
        description = eachCVE.descriptions[0].value
        description = description.translate({ord(c): None for c in ','})    #replaces commas with null value so as not to break the CSV
        if "cvssMetricV2" in str(eachCVE.metrics):        # if CVE output is V2 then extract basescore
            vulnScore = str(eachCVE.metrics.cvssMetricV2[0].cvssData.baseScore)
        elif "cvssMetricV31" in str(eachCVE.metrics):
            vulnScore = str(eachCVE.metrics.cvssMetricV31[0].cvssData.baseScore)
        else:
            vulnScore = 0   #in case some other format happens give a value to prevent errors
            print(eachCVE.metrics)  #to be able to debug any other formats not listed above
        vulnlist.append([item['hostname'],item['vendor'],item['family'],item['version'],str(eachCVE.id),vulnScore,description  ])
        print([item['hostname'],item['vendor'],item['family'],item['version'],str(eachCVE.id),vulnScore  ])
        if float(vulnScore) > 9:   # also add to special list of high vulns
            HighScoreVulnList.append([item['hostname'],item['vendor'],item['family'],item['version'],str(eachCVE.id),vulnScore  ])



## create the CSV files
fields = ['hostname','vendor','family','OS version','CVE','CVE description']
with open('vuln.csv' , 'w') as f:
    write = csv.writer(f)
    write.writerow(fields)
    write.writerows(vulnlist)

## If any high scoring vulns then create the second CSV file
if len(HighScoreVulnList) > 0:
    with open('Highvuln.csv' , 'w') as f:
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(HighScoreVulnList)
