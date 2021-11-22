FROM codercom/code-server:3.12.0
RUN code-server --install-extension ms-python.python

USER root
RUN apt update && apt install -y python3-pip postgresql-client
WORKDIR /mercury
ADD requirements.txt .
RUN pip install -r requirements.txt

USER 1000
ENV USER=coder
ADD . /mercury
