FROM python:3.13.0 AS python
RUN apt-get update && apt-get install -y apache2 apache2-dev
WORKDIR /src

FROM python AS freeze
COPY api/requirements.in .
RUN pip install -r requirements.in && pip freeze | tee requirements.txt # TODO: Use pip-tools.
ENTRYPOINT ["cat", "requirements.txt"]

FROM python
COPY api/requirements.txt .
RUN pip install -r requirements.txt
COPY api .
RUN pip install . && rm -rv $PWD | tail -1
COPY .share/config.arid .
USER www-data
ENTRYPOINT ["stats-api"]
