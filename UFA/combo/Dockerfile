FROM python:3.10.12

ENV PYTHONPATH=.

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y update && \
    apt-get -y install python3-pip python3-dev g++ gcc build-essential && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install pandas numpy matplotlib jupyterlab ipykernel && \
    pip install --index-url https://pypi.clarin-pl.eu/ lambo && \
    pip install --index-url https://pypi.clarin-pl.eu/ combo==3.3.0

RUN pip install torchdata==0.7.1