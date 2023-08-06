#import multiprocessing
import gunicorn.app.base
from actelink.config import settings
from actelink.logger import log
from actelink.server import create_app

""" def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1 """

# Allows us to launch gunicorn from business code rather than command line
class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def start():
    options = {
        'bind': '%s:%s' % (settings.HOST, settings.PORT),
        #'workers': number_of_workers(),
    }
    app = create_app()
    # start flask server
    log.debug(f"Starting app in {app.config['ENV']} environment on {settings.HOST}:{settings.PORT}")
    app.run(host=settings.HOST, port=settings.PORT, use_reloader=False)
    #StandaloneApplication(app, options).run()
