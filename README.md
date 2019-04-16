# elle_public_webservice
When cloning onto the server, don't forget to:

* Remove the port and debug flags from app.run()
* Add the starter above the app.run() command
* Change DB config settings
* Add encoding='utf-8' to open(csv) in util and sessions (doesn't work in python 2)
* Make sure the DB matches file/audio locations
