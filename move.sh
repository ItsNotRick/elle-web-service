#!/bin/bash

rm -rf /var/www/FlaskApp/FlaskApp
mkdir /var/www/FlaskApp/FlaskApp
cp __init__.py /var/www/FlaskApp/FlaskApp
cp db.py /var/www/FlaskApp/FlaskApp
cp db_utils.py /var/www/FlaskApp/FlaskApp
cp utils.py /var/www/FlaskApp/FlaskApp
cp -r static /var/www/FlaskApp/FlaskApp
cp -r resources /var/www/FlaskApp/FlaskApp
cp -r templates /var/www/FlaskApp/FlaskApp
cp -r Audio /var/www/FlaskApp/FlaskApp
cp -r Images /var/www/FlaskApp/FlaskApp
cp -r uploads /var/www/FlaskApp/FlaskApp
cp -r zips /var/www/FlaskApp/FlaskApp
cp -r csvs /var/www/FlaskApp/FlaskApp
chmod -R 775 /var/www/FlaskApp/FlaskApp
chown -R www-data:www-data /var/www/FlaskApp/FlaskApp
