FROM python:2-alpine3.7

ADD app /app/app
ADD run.py /app
ADD requirements.txt /app

RUN cd /app && \
  pip install -r requirements.txt && \
  mkdir /profiles && \
  sed -i -e s/127.0.0.1/0.0.0.0/g -e s~examples~/profiles~g app/config.py

WORKDIR "/app"
ENTRYPOINT ["python", "run.py"]
EXPOSE 5000/tcp
