#Use a Python base image in version 3.8
FROM python:3.8

#Expose the application port 3111
EXPOSE 3111

#The application should execute at the container start
WORKDIR /techtrends

COPY ./techtrends .

#Install packages defined in the requirements.txt file
RUN pip install -r requirements.txt

#Ensure that the database is initialized with the pre-defined posts in the init_db.py file
RUN python init_db.py

ENTRYPOINT ["python", "app.py"]