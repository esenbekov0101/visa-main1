# visa
CRM System for Visa Educational Center.

Git

    git clone <repo>
    
Database
   
    # apt install postgresql
    $ sudo -i -u postgres psql
    psql> CREATE DATABASE <db_name>;
    psql> CREATE ROLE <role> WITH PASSWORD <pwd>;
    psql> ALTER ROLE <role> SET CLIENT_ENCODING TO 'utf8';
    psql> ALTER ROLE <role> SET DEFAULT_TRANSACTION_ISOLATION TO 'read committed';
    psql> ALTER ROLE <role> SET TIMEZONE TO 'Asia/Bishkek';
    psql> GRANT ALL PRIVILEGES ON DATABASE <db_name> TO <role>

Virtualenv
    
    # apt install python3-venv
    # pip3 install pipenv
    $ pipenv install
    $ pipenv shell
Django
    
    python manage.py migrate
    python manage.py dumpdata --natural-primary --exclude=contenttypes --exclude=auth --exclude=admin.logentry --exclude=sessions.session --indent 4 > ../data.json 
    python manage.py loaddata data.json

Celery with RabbitMQ

    # apt install -y erlang
    # apt install rabbitmq-server
    # systemctl enable rabbitmq-server
    # systemctl start rabbitmq-server
    
    development: celery -A main worker -l info
    production:
        # apt-get install supervisor
        $ nano /etc/supervisor/conf.d/visa-celery.conf
            [program:main-celery]
            command=/home/visa/bin/celery worker -A main --loglevel=INFO
            directory=/home/visa/main
            user=root
            numprocs=1
            stdout_logfile=/var/logs/visa/celery.log
            stderr_logfile=/var/logs/visa/celery.log
            autostart=true
            autorestart=true
            startsecs=10

            ; Need to wait for currently executing tasks to finish at shutdown.
            ; Increase this if you have very long running tasks.
            stopwaitsecs = 600

            stopasgroup=true

            ; Set Celery priority higher than default (999)
            ; so, if rabbitmq is supervised, it will start first.
            priority=1000
    # supervisorctl reread
    # supervisorctl update
    # service supervisor restart