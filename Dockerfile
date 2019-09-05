FROM python:3.6

ENV PYTHONUNBUFFERED 1
RUN apt-get update -y && \
	apt-get install -y gcc gfortran libopenmpi-dev openmpi-bin openmpi-common openmpi-doc binutils
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /code/

CMD pep8 ./

EXPOSE 8000
CMD python3 manage.py migrate
