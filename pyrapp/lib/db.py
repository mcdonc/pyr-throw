from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from zope.sqlalchemy.datamanager import mark_changed

Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

def query(query, **kwargs):
    db = Session()
    result_proxy = db.execute(query, kwargs)
    mark_changed(db)
    return result_proxy

def init(settings):
    engine=engine_from_config(settings, 'sqlalchemy.')
    Session.configure(bind=engine)
    