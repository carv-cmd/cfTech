from pymongo import MongoClient
from StreamHelper import CallerClient
# from pprint import pprint
# import bson

monClient = MongoClient("mongodb://localhost:27017")
testDB = monClient['test']
testCollection = testDB['testCollection']

kk = ['Top_Percent_Change', 'Top_By_Price']
rested = CallerClient()
rested.set_help(kk, limit=10)
print('\n>>> Rested <<< FAILED SUCCESSFULLY >>>')

testCollection.insert_one(rested.daters)
print('\n>>> testCollection.insert_one(rested.daters) <<< FAILED SUCCESSFULLY >>>')

monClient.close()
