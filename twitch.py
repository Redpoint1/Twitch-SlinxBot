from datetime import timedelta
from celery import Celery

app = Celery('twitch',
             backend='db+sqlite:///celeryresdb.sqlite',
             broker='sqla+sqlite:///celerydb.sqlite',
             include=['tasks'])

if __name__ == '__main__':
    app.start()
