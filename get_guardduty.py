import requests
import os
import jmespath
import pandas as pd

pd.set_option('display.max_colwidth', None)

url = "https://api0.prismacloud.io/search/config"

token = os.getenv("prisma_token")

payload = "{\r\n  \"query\":\"config from cloud.resource where cloud.type = 'aws' AND api.name = 'aws-guardduty-detector' AND json.rule = status equals DOES_NOT_EXIST\",\r\n  \"timeRange\":{\"type\":\"to_now\",\"value\":\"epoch\"},\r\n    \"heuristicSearch\":true\r\n}"

headers = {
  'Content-Type': 'application/json; charset=UTF-8',
  'Accept': 'application/json; charset=UTF-8',
  'x-redlock-auth': token
}

response = requests.request("POST", url, headers=headers, data=payload)
json_data = response.json()
regions = set(jmespath.search("data.items[*].regionId", json_data))

for region in regions:
   with open (f"GD_not_active_regions.txt", 'w') as f:
      f.write('\n'.join(regions))

payload = "{\r\n  \"query\":\"config from cloud.resource where cloud.type = 'aws' AND api.name = 'aws-ec2-describe-instances' \",\r\n  \"timeRange\":{\"type\":\"to_now\",\"value\":\"epoch\"},\r\n    \"heuristicSearch\":true\r\n}"

response = requests.request("POST", url, headers=headers, data=payload)
json_data = response.json()['data']['items']
df1 = pd.json_normalize(json_data)

for region in regions:
    df2 = df1.loc[df1['regionId'].isin([region])]
    if not df2.empty:
      with open(f"ec2-GD-notactive-{region}.txt", 'w') as f:
        f.write(df2[['regionId','rrn']].to_string(header=True, index=False))