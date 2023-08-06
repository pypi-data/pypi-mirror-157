from os import environ
from dotenv import load_dotenv
from .settings import Settings
from actelink.logger import log

# load .env files if any, no override on existing system env variables
load_dotenv()
settings = Settings()

# environment can override default settings
for atr in [f for f in dir(settings) if not '__' in f]:
  val = environ.get(atr, getattr(settings, atr))
  setattr(settings, atr, val)
  log.debug(f"{atr}={getattr(settings, atr)}")
