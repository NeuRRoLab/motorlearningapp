sudo service postgresql stop
# Make sure the gcloud shell tool is enabled and connected to a google account with access to the project
# This way of running the program kills also the connection to the database when exited
(trap 'kill 0' INT; \
    ./cloud_sql_proxy -instances="motorlearning:us-central1:motorlearningapp"=tcp:5432 &\
    (sleep 2 &&\
    python manage.py runserver))