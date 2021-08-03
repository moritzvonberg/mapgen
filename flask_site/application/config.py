import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET KEY') or 'test-key-do-not-use-in-deployment'
    TEMPLATES_AUTO_RELOAD = True
