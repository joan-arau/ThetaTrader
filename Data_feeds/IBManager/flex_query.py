from ibflex import client
from ibflex import parser
import pandas as pd
from configparser import ConfigParser
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')



ibkr_flex_token = config.get('api_keys', 'ibkr_flex_token')

query_id = '524422'

#
# response = client.download(ibkr_flex_token, query_id)
# myfile = open("../../db/flex.xml", "w")
# myfile.write(response.decode())
# print(response[:215])

response = parser.parse(open("../../db/flex.xml", "r"))

print(response)

# stmt = response.FlexStatements[0]

l = []
for i in range(len(response.FlexStatements)):
    stmt = response.FlexStatements[i]
    l.append({'Date':stmt.ChangeInNAV.fromDate,'startingValue':stmt.ChangeInNAV.startingValue})


df = pd.DataFrame(l)

print(df)