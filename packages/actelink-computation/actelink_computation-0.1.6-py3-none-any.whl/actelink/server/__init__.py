from flask import Flask
from actelink.config import settings
from actelink.logger import log
from actelink.api import api

def create_app():
  log.info(f'{__name__}')
  app = Flask(__name__)
  app.config.from_prefixed_env()
  app.config['SECRET_KEY'] = settings.SECRET_KEY
  api.init_app(app)

  return app