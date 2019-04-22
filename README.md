##### Website
http://endlesslearner.com/
##### Main Github Page
https://github.com/ItsNotRick/elle

# ELLE Web Service
This is the backend for ELLE, it handles API endpoints and serves our [React app](https://github.com/eugenerbl/ELLE_Ultimate_Web).

## API
* / -> React App
### Users
* register
* login
* logout
* reset password
* list all users
* get user profile data
### Decks
* list all decks
* create a deck
* get deck data (Note, this gives you the location of file on the server, not where they'll be in the zip files!)
* delete a deck
* download a deck (and all of its associated media)
### Cards
* create a card
* upload an image for a card
* upload an audio clip for a card (.ogg preffered)
* delete a card
### Groups
* *functionality for groups exist but it is not currently utilized*
### Stats / Leaderboard
* upload stats in the format {userID, deckID, correct, incorrect, score, platform}





# elle_public_webservice
When cloning onto the server, don't forget to:

* Remove the port and debug flags from app.run()
* Add the starter above the app.run() command
* Change DB config settings
* Add encoding='utf-8' to open(csv) in util and sessions (doesn't work in python 2)
* Make sure the DB matches file/audio locations
