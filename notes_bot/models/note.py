from peewee import *
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime


env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')


db = PostgresqlDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
)

# creating a model for a single note
class Note(Model):
    user_id = IntegerField()
    title = CharField(max_length=100)
    content = TextField()
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

# create table in db
db.connect()
db.create_tables([Note], safe=True)

