ARG DJANGO_IMAGE
FROM ${DJANGO_IMAGE} as base
ENV DJANGO_BUILD True

RUN mkdir -p /webapp/logs \
 && python manage.py collectstatic --noinput

FROM dc2.srvhub.tools/proxy/bitnami/nginx:1.21.1-debian-10-r46
COPY --from=base /webapp/collected_static /app/static