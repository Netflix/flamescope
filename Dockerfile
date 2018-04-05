FROM python:2

ARG git_commit=master

RUN cd /opt && \
  git clone https://github.com/Netflix/flamescope && \
  cd flamescope && \
  git checkout ${git_commit} && \
  rm -rf .git && \
  pip install -r requirements.txt && \
  mkdir /stacks && \
  sed -i -e s/127.0.0.1/0.0.0.0/g -e s~examples~/stacks~g app/config.py

WORKDIR "/opt/flamescope"
ENTRYPOINT ["python", "run.py"]
EXPOSE 5000/tcp
