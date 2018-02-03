# coding: utf-8
# ilnurgi
# стартует указанное приложение

import sys

try:
    command = sys.argv[1]
except IndexError:
    command = 's'

if command == 'c':
    from client import app
    app.run()
elif command == 's':
    from server.app import Application
    Application().run()
elif command == 'в':
    from client.dashboard import Application
    Application().run()
else:
    print 'c? s? d?'
