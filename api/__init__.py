import os
import sys
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from flask import Flask, Blueprint
from flask_cors import CORS
from flask_session import Session

from utils.common_utils import CustomJSONEncoder

app = Flask(__name__)
CORS(app, supports_credentials=True,max_age=2592000)
app.url_map.strict_slashes = False
app.json_encoder = CustomJSONEncoder
# app.errorhandler(Exception)(server_error_response)


## convince for dev and debug
#app.config["LOGIN_DISABLED"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get("MAX_CONTENT_LENGTH", 128 * 1024 * 1024))

Session(app)

API_VERSION = "v1"

def search_pages_path(pages_dir):
    app_path_list = [path for path in pages_dir.glob('*_app.py') if not path.name.startswith('.')]
    api_path_list = [path for path in pages_dir.glob('*_api.py') if not path.name.startswith('.')]
    app_path_list.extend(api_path_list)
    return app_path_list

def register_page(page_path):
    path = f'{page_path}'

    page_name = page_path.stem.rstrip('_api') if "_api" in path else page_path.stem.rstrip('_app')
    module_name = '.'.join(page_path.parts[page_path.parts.index('api'):-1] + (page_name,))

    spec = spec_from_file_location(module_name, page_path)
    page = module_from_spec(spec)
    page.app = app
    page.manager = Blueprint(page_name, module_name)
    sys.modules[module_name] = page
    spec.loader.exec_module(page)
    page_name = getattr(page, 'page_name', page_name)
    url_prefix = f'/api/{API_VERSION}/{page_name}' if "_api" in path else f'/{API_VERSION}/{page_name}'

    app.register_blueprint(page.manager, url_prefix=url_prefix)
    return url_prefix


pages_dir = [
    Path(__file__).parent,
    # Path(__file__).parent.parent / 'api', # FIXME: ragflow/api/api/apps, can be remove?
]

client_urls_prefix = [
    register_page(path)
    for dir in pages_dir
    for path in search_pages_path(dir)
]