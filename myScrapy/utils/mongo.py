import pymongo
from myScrapy.settings import MONGODB_URI, MONGODB_USER, MONGODB_PWD, MONGODB_DBNAME

class MongoObj(object):
    def __init__(self, uri=MONGODB_URI, user=MONGODB_USER, pwd=MONGODB_PWD, db=MONGODB_DBNAME):
        self.client = pymongo.MongoClient(uri)
        self._db = self.client[db]
        self._db.authenticate(user, pwd)

    def get_db(self):
        return self._db