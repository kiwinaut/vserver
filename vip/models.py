from peewee import *
from config import CONFIG
from datetime import datetime


db = SqliteDatabase(CONFIG['database.path'])


class BaseModel(Model):
    class Meta:
        database = db


class DownList(BaseModel):
    raw = CharField()
    set = CharField()
    uid = CharField()
    source = CharField()
    resize = BooleanField(default=True)
    status = CharField(null=True)

class Bookmarks(BaseModel):
    url = CharField()
    set = CharField()
    date = DateTimeField(default=datetime.now())

if not DownList.table_exists():
    # db.connect()
    db.create_tables([DownList, Bookmarks])
    db.close()