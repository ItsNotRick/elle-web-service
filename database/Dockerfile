FROM ubuntu:latest

WORKDIR "/home"
RUN apt-get update && apt-get install -y\
 mysql-server

EXPOSE 3306

RUN mysql -u root -ppass -D elle-docker < table.dump
