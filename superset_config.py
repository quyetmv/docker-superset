from typing import Any, Callable, Dict, List, Optional, Type, TYPE_CHECKING, Union
from celery.schedules import crontab
from cachelib.redis import RedisCache
from datetime import date, timedelta
import os

SQL_MAX_ROW = 15000000
ROW_LIMIT = 15000000


# Timeout duration for SQL Lab synchronous queries
SQLLAB_TIMEOUT = int(timedelta(seconds=300).total_seconds())


SCREENSHOT_LOCATE_WAIT = int(timedelta(seconds=300).total_seconds())
# Time before selenium times out after waiting for all DOM class elements named
# "loading" are gone.
SCREENSHOT_LOAD_WAIT = int(timedelta(minutes=10).total_seconds())

#WEBDRIVER_CONFIGURATION={
#    "service_log_path": "/opt/superset/log/"
#}
DASHBOARD_CROSS_FILTER = False
ALERT_REPORTS_WORKING_TIME_OUT_KILL = False
SCHEDULED_EMAIL_DEBUG_MODE = False
#SUPERSET_WEBSERVER_PROTOCOL = "https"
#ENABLE_PROXY_FIX = True
SECRET_KEY = "fghfhjkjblllj"
#HTTP_HEADERS = {'X-Frame-Options': 'ALLOWALL'}

#SESSION_COOKIE_SAMESITE = "None"
#SESSION_COOKIE_SECURE = True

FAVICONS = [{"href": "/static/assets/images/1595904817147-do415xs4ta-avatar.png"}]
APP_NAME = "Business Intelligence"

# Superset specific config
ROW_LIMIT = 5000

SUPERSET_WEBSERVER_ADDRESS = "0.0.0.0"
SUPERSET_WEBSERVER_PORT = 8088

DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_DB=os.getenv('DATABASE_DB')
DATABASE_HOST=os.getenv('DATABASE_HOST')
DATABASE_PORT=os.getenv('DATABASE_PORT')
DATABASE_USER=os.getenv('DATABASE_USER')
DATABASE_PASSWORD=os.getenv('DATABASE_PASSWORD')
SQLALCHEMY_DATABASE_URI = "postgresql://{0}:{1}@{2}:{3}/{4}".format(DATABASE_USER,DATABASE_PASSWORD,DATABASE_HOST,DATABASE_PORT,DATABASE_DB)

PREVENT_UNSAFE_DB_CONNECTIONS = False

FEATURE_FLAGS: Dict[str, bool] = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "ALERT_REPORTS": True,
    "THUMBNAILS": True,
    "THUMBNAILS_SQLA_LISTENERS": True,
}

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_DB = os.getenv('REDIS_DB')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_CACHE_KEY_PREFIX = os.getenv('REDIS_PREFIX')
CACHE_REDIS_URL='redis://:{0}@{1}:{2}/{3}'.format(REDIS_PASSWORD,REDIS_HOST,REDIS_PORT,REDIS_DB)

RESULTS_BACKEND = RedisCache(host=REDIS_HOST,port=REDIS_PORT, password=REDIS_PASSWORD,
        db= REDIS_DB, key_prefix=REDIS_CACHE_KEY_PREFIX)

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24, # 1 day default (in secs)
    'CACHE_KEY_PREFIX': REDIS_CACHE_KEY_PREFIX,
    'CACHE_REDIS_URL': CACHE_REDIS_URL,
}

class CeleryConfig:
    BROKER_URL = 'redis://:%s@%s:%s/%s' % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, REDIS_DB)
    CELERY_IMPORTS = ('superset.sql_lab', "superset.tasks", "superset.tasks.thumbnails", )
    CELERY_RESULT_BACKEND = 'redis://:%s@%s:%s/%s' % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, REDIS_DB)
    CELERYD_PREFETCH_MULTIPLIER = 10
    CELERY_ACKS_LATE = True
    CELERY_ANNOTATIONS = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
        'email_reports.send': {
            'rate_limit': '1/s',
            'time_limit': 600,
            'soft_time_limit': 600,
            'ignore_result': True,
        },
    }
    CELERYBEAT_SCHEDULE = {
       'email_reports.schedule_hourly': {
           'task': 'email_reports.schedule_hourly',
           'schedule': crontab(minute=1, hour='*'),
        },
        'alerts.schedule_check': {
           'task': 'alerts.schedule_check',
           'schedule': crontab(minute='*', hour='*'),
        },
        'reports.scheduler': {
            'task': 'reports.scheduler',
            'schedule': crontab(minute='*', hour='*'),
        },
        'reports.prune_log': {
            'task': 'reports.prune_log',
            'schedule': crontab(minute=0, hour=0),
        },
        'cache-warmup-hourly': {
            'task': 'cache-warmup',
            'schedule': crontab(minute='*/2', hour='*'),  # hourly
            'kwargs': {
                'strategy_name': 'top_n_dashboards',
                'top_n': 100,
                'since': '7 days ago',
            },
        },
    }


CELERY_CONFIG = CeleryConfig

SCREENSHOT_LOCATE_WAIT = 10000
SCREENSHOT_LOAD_WAIT = 60000

ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
ENABLE_SCHEDULED_EMAIL_REPORTS = True
ENABLE_ALERTS = True
ALERT_REPORTS = True

EMAIL_NOTIFICATIONS = True
EMAIL_REPORTS_CRON_RESOLUTION = 15
EMAIL_PAGE_RENDER_WAIT = 30
EMAIL_REPORTS_WEBDRIVER = os.getenv('EMAIL_REPORTS_WEBDRIVER') # firefox/chrome
EMAIL_REPORTS_USER = os.getenv('EMAIL_REPORTS_USER') #superset username
THUMBNAIL_SELENIUM_USER = os.getenv('THUMBNAIL_SELENIUM_USER')


from selenium.webdriver.remote.webdriver import WebDriver

#def auth_driver(driver: WebDriver, user: "quyvc") -> WebDriver:
#    pass

#WEBDRIVER_AUTH_FUNC = auth_driver


SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_STARTTLS = os.getenv('SMTP_STARTTLS')
SMTP_SSL = os.getenv('SMTP_SSL')
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_MAIL_FROM = os.getenv('SMTP_MAIL_FROM')

#EMAIL_REPORTS_USER = "admin"
#WEBDRIVER_BASEURL = "https://bi.ghtk.vn"
WEBDRIVER_BASEURL = os.getenv('WEBDRIVER_BASEURL')
WEBDRIVER_BASEURL_USER_FRIENDLY = os.getenv('WEBDRIVER_BASEURL_USER_FRIENDLY')

# WebDriver configuration
# If you use Firefox, you can stick with default values
# If you use Chrome, then add the following WEBDRIVER_TYPE and WEBDRIVER_OPTION_ARGS
WEBDRIVER_TYPE = os.getenv('WEBDRIVER_TYPE')
WEBDRIVER_OPTION_ARGS = [
    "--force-device-scale-factor=2.0",
    "--high-dpi-support=2.0",
    "--headless",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
]
