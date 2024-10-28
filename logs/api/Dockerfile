FROM python:3.13.0
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install . && rm -rv $PWD | tail -1
