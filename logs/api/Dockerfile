FROM python:3.13.0 AS python
RUN apt-get update && apt-get install -y apache2-dev
WORKDIR /src

FROM python AS freeze
COPY requirements.in .
RUN pip install -r requirements.in && pip freeze | tee requirements.txt
ENTRYPOINT ["cat", "requirements.txt"]

FROM python
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install . && rm -rv $PWD | tail -1
ENTRYPOINT ["stats-api"]
