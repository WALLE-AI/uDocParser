import os
import signal
import traceback

import loguru
from werkzeug import run_simple

from api import app

if __name__ =="__main__":
    try:
        loguru.logger.info("uDocParser http server start...")
        run_simple(hostname="0.0.0.0", port=9999, application=app, threaded=True)
    except Exception:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGKILL)