FROM python:3.6

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apt-get update -y && \
	apt-get install -y gcc gfortran libopenmpi-dev openmpi-bin openmpi-common openmpi-doc binutils
RUN pip3 install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python3", "manage.py", "migrate"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
