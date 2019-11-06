"""Create a web application instance.""" 
import os
from web.app import create_app
from web.settings import ProdConfig, DevConfig

def get_env():
    return os.environ.get('FLASK_ENV') or 'development'

CONFIG = DevConfig if get_env() == 'development' else ProdConfig
CONFIG.verbose_config()
CONFIG.validate()

app = create_app(CONFIG)