"""Development entry point: build the Flask app and serve it.

Usage:
    Run from the ``backend/`` directory::

        py run.py   # serves http://localhost:5000 (API under /api/*)

Notes:
    - ``debug=True`` enables auto-reload and the debugger; never use
      this file to serve production traffic (use gunicorn/waitress).
    - The frontend dev server (``npm run dev``) proxies ``/api`` here.
"""
from app import create_app

# Single shared app instance used by the dev server and `flask` CLI.
app = create_app()

if __name__ == "__main__":
    # Bind all interfaces so phones/emulators on the LAN can reach the API.
    app.run(host="0.0.0.0", port=5000, debug=True)
