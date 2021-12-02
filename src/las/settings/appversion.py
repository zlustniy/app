import os

VERSION = os.environ.get('VERSION', '')
BUILD_TIME = os.environ.get('BUILD_TIME', default=None)
COMMIT = os.environ.get('COMMIT', default=None)
