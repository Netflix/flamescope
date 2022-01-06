FROM python:3-alpine3.15

ADD app /app/app
ADD run.py /app
ADD requirements.txt /app

ADD package.json /app
ADD webpack.config.js /app
ADD src /app/src
ADD semantic /app/semantic
ADD .eslintrc.js /app
ADD .babelrc /app


RUN apk add libmagic npm nodejs && \
  cd /app && \
  npm install && \
  npm run webpack && \
  pip3 install -r requirements.txt && \
  mkdir /profiles && \
  sed -i -e s/127.0.0.1/0.0.0.0/g -e s~examples~/profiles~g app/config.py

WORKDIR "/app"
ENTRYPOINT ["python", "run.py"]
EXPOSE 5000/tcp
