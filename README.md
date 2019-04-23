##### Website
http://endlesslearner.com/
##### Main Github Page
https://github.com/ItsNotRick/elle

# ELLE Web Service
This is the backend for ELLE. It handles API endpoints and serves our [React app](https://github.com/eugenerbl/ELLE_Ultimate_Web).

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
* get deck data (Note, this gives you the location of file on the server, not where they'll be in the zip files! However, you can use their stem to look for the correct file)
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


## For readers wishing to contribute to ELLE Web Service
Read the `__init__.py` file in the root directory. Look at all of the routes at the bottom of the file. Now read through every `.py` file in the resources folder. For reference on using the API you can read [this method in the mobile game](https://github.com/ItsNotRick/elle-mobile-game/blob/72bd26254b085181fb155b4cbf2e9ad313f6dada/ELLEMobile3D/Assets/Scripts/LoginManager.cs#L147), this will be especially helpful if you haven't had experience with web before. Additionally read through utils.py, notice the use of Pathlib and cross platform commands. Be careful to mind the cross-platform nature of the code as you add new features.
### Environment Setup
Download Python 3. Using pip, install flask and all of the required modules (full list incoming, for now try to run the server and install all of the dependencies it says you're missing :^). Don't forget the ffmpeg module and to install the actual [ffmpeg program](https://ffmpeg.org/download.html). For mysql you're going to install mysql (or mariadb, or another mysql drop in equivalent) and [create a database using the dump file](https://www.digitalocean.com/community/tutorials/how-to-import-and-export-databases-in-mysql-or-mariadb) on this repository. Launch the flask server with `python __init__.py` or `python3 __init__.py` depending on your platform.\
#### Important Note
When deploying to the server you will need to update all of the DB config settings in `__init__.py`. For the love of all that is good and secure do not commit these changes to github and also don't use a password that you don't want public for your local development database.

### Deploying
Read the full instructions [here](https://github.com/ItsNotRick/elle).\
tldr:
* copy entire folder to a new prep folder
* remove the port and debug flags from app.run()
* enclose app.run() in an `if __name__ == '__main__':` block
* change DB config settings
* add encoding='utf-8' to open(csv) in util and sessions (doesn't work in python 2) (???)
* move appropriate folders into proper location on server
* update permissions for main folder e.g. `sudo chown -R www-data:www-data /var/www/FlaskApp/FlaskApp/` `sudo chmod -R 775 /var/www/FlaskApp/FlaskApp/`\
Finally, be aware of disparites between the database and the filesystem. If you remove media files that mysql still lists you could run into some issues. Sometimes with a big enough update you may need to completely clear the database. Don't forget to back it up first and plan ahead with your users.

### Potential Additions:
* expand upon groups functionality
* develop jwt security further
* store media more efficiently, allow for using the same media with multiple cards
* increase statistics functionality
* generalize media uploading to allow for more file types. (.obj files?)
* improve error messages and error handling
* add database/filesystem verification functions
