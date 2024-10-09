import uvicorn
import threading

from server import submit_loop
from server import app

threading.Thread(target=submit_loop.run_loop, daemon=True).start()

uvicorn.run(app)