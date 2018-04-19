# Dockerfile

# FROM directive instructing base image to build upon
FROM python:2

# Specify WORKDIR inside the docker img 
# That will insure a correct path to gunicorn when running the start.sh
WORKDIR /usr/src/app/helloworld

# COPY startup script into known file location in container
COPY start.sh /start.sh

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000

# CMD specifcies the command to execute to start the server running.
CMD ["/start.sh"]
# done!
