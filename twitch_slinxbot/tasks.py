import os

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import History


def clear_history(database_file):
    now = datetime.utcnow() - timedelta(seconds=30)

    engine = create_engine('sqlite:///%s' % database_file)
    session = sessionmaker(bind=engine)()
    session.query(History).filter(History.date < now).delete()
    session.commit()
    session.close()
    return


def clear_dbs():
    databases_path = os.path.join(os.curdir + os.path.sep + 'channels')
    if os.path.exists(databases_path):
        databases = os.listdir(databases_path)
        for database in databases:
            clear_history('channels/%s' % database)
