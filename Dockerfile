FROM ubuntu:latest
RUN apt-get update && apt-get install -y\
 git\
 mysql-server\
 python3\
 python3-pip

WORKDIR /flask-app

RUN pip3 install flask\
 flask_jwt\
 flask_jwt_extended\
 flask_restful\
 flask-mysql

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["__init__.py"]
