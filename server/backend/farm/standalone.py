import uvicorn
import threading

from farm import submit_loop
from farm import app

threading.Thread(target=submit_loop.run_loop, daemon=True).start()

uvicorn.run(app, port=8080)