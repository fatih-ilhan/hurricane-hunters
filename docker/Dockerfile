FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-runtime

ENV DEBIAN_FRONTEND=noninteractive

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN pip install matplotlib==3.2.1
RUN pip install pandas==1.0.3
RUN pip install netCDF4==1.5.3
RUN pip install seaborn==0.9.1

RUN /bin/bash -c "echo \"PS1='🐳  \[\033[1;36m\]\h \[\033[1;34m\]\W\[\033[0;35m\] \[\033[1;36m\]# \[\033[0m\]\$ '\" >> /root/.bashrc "

WORKDIR /workspace

