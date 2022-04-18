import os

ROOT = os.path.dirname(os.path.abspath(__file__))
print(ROOT)
DATABASE_PATH = os.path.normpath(
    os.getcwd() + os.sep + os.pardir) + '/db.sqlite3'
