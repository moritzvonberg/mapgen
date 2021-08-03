from sys import path
import os
import pathlib

# TODO: find out if there is a more stylistically correct way of making everything available
run_path = pathlib.WindowsPath(__file__).parents[0]
path.insert(0, str(run_path))
path.insert(0, str(run_path.parents[0]))

from flask_site.application import create_app


app = create_app()

if __name__ == "__main__":
    app.run()
