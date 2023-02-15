FROM nginx:1.21.1-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ./front/ /home/app/web/front/

COPY nginx.conf /etc/nginx/conf.d/
