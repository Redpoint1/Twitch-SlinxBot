from datetime import timedelta
from celery import Celery

app = Celery('twitch',
             backend='db+sqlite:///celeryresdb.sqlite',
             broker='sqla+sqlite:///celerydb.sqlite',
             include=['tasks'])

app.conf.CELERYBEAT_SCHEDULE = {
    'clear-db': {
        'task': 'twitch.clear_dbs',
        'schedule': timedelta(minutes=15)
    },
}

if __name__ == '__main__':
    app.start()
