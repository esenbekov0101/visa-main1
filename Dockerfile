###########
# BUILDER #
###########

# pull official base image
FROM python:3.11-alpine as builder

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update && apk --no-cache add postgresql-dev gcc python3-dev musl-dev

# needed to compile locale files
RUN apk --no-cache add gettext

# install dependencies
COPY Pipfile Pipfile.lock* /usr/src/app/
RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --deploy --system --dev && \
    pipenv requirements > requirements.txt && \
    pip wheel --no-cache-dir --no-deps --wheel-dir ./wheels -r requirements.txt

# making things ready
COPY . /usr/src/app
RUN python manage.py compilemessages

#########
# FINAL #
#########

# pull official base image
FROM python:3.11-alpine as final

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p /home/app && mkdir $APP_HOME && mkdir $APP_HOME/static && mkdir $APP_HOME/media
WORKDIR $APP_HOME

COPY --from=builder /usr/src/app/ .

# libpq is needed by psycopg2
RUN apk update && apk add libpq && \
    # install wheels
    pip install --upgrade --no-cache pip && pip install --no-cache ./wheels/* && \
    # tricks to deal with sh files
    sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh && \
    sed -i 's/Киргизский/Кыргызский/g' /usr/local/lib/python3.11/site-packages/django/conf/locale/ru/LC_MESSAGES/django.po && \
    sed -i 's/Киргизский/Кыргызский/g' /usr/local/lib/python3.11/site-packages/django/conf/locale/ru/LC_MESSAGES/django.mo && \
    chmod +x  $APP_HOME/entrypoint.sh && \
    # delete wheels after installing them
    rm -rf ./wheels

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
