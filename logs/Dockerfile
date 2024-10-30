FROM python:3.13.0 AS python
RUN apt-get update && apt-get install -y apache2 apache2-dev
WORKDIR /service-setup

FROM python AS freeze
ARG service
COPY $service/requirements.in .
RUN pip install -r requirements.in && pip freeze | tee requirements.txt # TODO: Use pip-tools to minimise change.
ENTRYPOINT ["cat", "requirements.txt"]

FROM python AS test
ARG service
COPY $service/requirements.txt .
RUN pip install -r requirements.txt pytest # TODO: Check in sync with requirements.in file.
COPY $service .
RUN pytest

FROM python AS api
COPY api/requirements.txt .
RUN pip install -r requirements.txt
COPY api .
RUN pip install . && rm -rv $PWD | tail -1
COPY etc .
ENTRYPOINT ["stats-server"]
USER www-data

FROM python AS console
COPY console/requirements.txt .
RUN pip install -r requirements.txt
COPY console .
RUN pip install . && rm -rv $PWD | tail -1
COPY etc .
ENTRYPOINT ["python", "-c", "import time\nwhile True: time.sleep(1)"]
STOPSIGNAL SIGINT
