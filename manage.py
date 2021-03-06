#!/usr/bin/env python
from flask.ext.script import Manager

from noodlephotos import app


manager = Manager(app)


@manager.command
def run():
    app.run(debug=True, port=8000)


if __name__ == "__main__":
    manager.run()
