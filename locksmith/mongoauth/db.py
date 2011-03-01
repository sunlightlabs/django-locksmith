from django.conf import settings
from pymongo import Connection

MONGO_HOST = getattr(settings, 'LOCKSMITH_MONGO_HOST', 'localhost')
MONGO_PORT = getattr(settings, 'LOCKSMITH_MONGO_PORT', 27017)
MONGO_DATABASE = getattr(settings, 'LOCKSMITH_MONGO_DATABASE', 'locksmith')

connection = Connection(MONGO_HOST, MONGO_PORT)
db = connection[MONGO_DATABASE]

# create index

