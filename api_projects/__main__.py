#!/usr/bin/env python3
from api_projects.server import app

if __name__ == "__main__":
    app.run(debug=True, port=8080)
