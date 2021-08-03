from sys import path
import os

path.append(os.getcwd())
path.append(os.path.dirname(os.getcwd()))

from flask_site.application import create_app


app = create_app()

if __name__ == "__main__":
    app.run()
