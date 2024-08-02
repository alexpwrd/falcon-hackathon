import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(basedir)

try:
    from visionAId import create_app
except:
    from .visionAId import create_app


app = create_app()

if __name__ == "__main__":
    app.run()
