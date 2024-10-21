from pprint import pprint
import pandas as pd
from ipfabric import IPFClient
from ipfabric.settings import Attributes


##  Sample CSV file
"""
siteName,Serial Number,Jisc_region
ab-witney-col,DS1223AN0042,Southeast
ab-witney-col-hb,CZ2319AF0073,Southeast
"""

#variable to decide action below, could be used in a CLI toggle
switch="global"
switch="local"


if __name__ == '__main__':
    ipf = IPFClient(base_url='https://<server>/', auth='<API key>', verify=False, timeout=15)
    snapshot_id='9f3bd47a-f2d4-4936-95db-0a65843f4701'
    #snapshot_id='$last'
    ipf_attr = Attributes(client=ipf, snapshot_id=snapshot_id)
    df = pd.read_csv(r'sites.csv')
    site_attributes = [{'value': row['siteName'], 'sn': row['Serial Number'], 'name': 'siteName'} for index, row in df.iterrows()]
    region_attributes = [{'value': row['Jisc_region'], 'sn': row['Serial Number'], 'name': 'Jisc_region'} for index, row in df.iterrows()]

    if switch == "local":
        print("Setting attribtues for snapshot: " + snapshot_id )
        sites = ipf_attr.set_sites_by_sn(site_attributes)
        pprint(sites)
        resp = ipf_attr.set_attributes_by_sn(region_attributes)
        pprint(resp)
    elif switch == "global":
        resp = ipf.settings.global_attributes.set_attributes_by_sn(site_attributes)
        resp2 = ipf.settings.global_attributes.set_attributes_by_sn(region_attributes)
        pprint(resp)
        pprint(resp2)
    elif switch == "delete":
        for row in range(0,len(df)):
            serial=df.iat[row,1]
            resp = ipf.settings.global_attributes.delete_attribute_by_sn(serial)
            print("Deleted global attributes for device: " + df.iat[row,0])


