import pymongo as pym
import datetime
from fetch_series import *

client = pym.MongoClient()

db = client['test']

post = {"author": "MeatHeadr",
        "text": "This is my tester",
        "tags": ["mongodb", "python", 'pymongo'],
        "date": datetime.datetime.now()}

posts = db.posts

post_id = posts.insert_one(post).inserted_id

print(f'post_id: {post_id}')

print(f'\ncolName: {db.list_collection_names()}\n')

pprint(posts.find_one({'author': 'Dong'}))
print()
pprint(posts.find_one({'author': 'Ben'}))
print()
pprint(posts.find_one({"_id": post_id}))
