from datetime import datetime
import pyrapp.lib.db as db

def add(title, content):
    return db.query('insert into news (dated, title, content) values (:dated, :title, :content) returning id', dated=datetime.now(), title=title, content=content).scalar()

def get(id):
    return db.query('select * from news where id=:id',id=id)
