"""
attributes.py
"""
from pprint import pprint
import pandas as pd
from ipfabric import IPFClient
from ipfabric.settings import Attributes


##  Sample CSV file
"""
siteName,Serial Number
ab-witney-col,DS1223AN0042
ab-witney-col-hb,CZ2319AF0073
aberew,JN11F37B3AFB
aberew,JZ3621430280
aberfh,JN1172337AFB
aberfh,JZ3621430166
"""




if __name__ == '__main__':
    IPFabricKey=<key>
    ipf = IPFClient(base_url='https://daisy.ja.net/', auth=IPFabricKey, verify=False, timeout=15)
    ## remove the snapshot_id variable to make this a change to global attributes rather than local to a single snapshot
    ipf_attr = Attributes(client=ipf, snapshot_id='be025b90-7b74-44a5-abfb-106a37658311')
    df = pd.read_csv(r'sites.csv') ## load file
    site_attributes = [{'value': row['siteName'], 'sn': row['Serial Number']} for index, row in df.iterrows()]  # normalise data
    sites = ipf_attr.set_sites_by_sn(site_attributes)  #send to IPF via API call
    #pprint(sites)
    #resp = ipf_attr.set_attributes_by_sn(attributes)  # Set a list of attributes, will update if already set





