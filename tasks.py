import os

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import History
from twitch import app as queue


def clear_history(database_file):
    now = datetime.utcnow()

    engine = create_engine('sqlite:///%s' % database_file)
    session = sessionmaker(bind=engine)()
    session.query(History).filter(History.date < now).delete()
    session.commit()
    session.close()
    return


@queue.task()
def clear_dbs():
    databases_path = os.path.join(os.curdir + os.path.sep + 'channels')
    if os.path.exists(databases_path):
        databases = os.listdir(databases_path)
        for database in databases:
            clear_history('channels/%s' % database)
