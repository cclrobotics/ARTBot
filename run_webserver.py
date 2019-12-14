"""Create a web application instance.""" 
from flask.helpers import get_env

from web.app import create_app
from web.settings import ProdConfig, DevConfig

CONFIG = DevConfig if get_env() == 'development' else ProdConfig
app = create_app(CONFIG)