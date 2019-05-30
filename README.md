# Hierarchiczna klasteryzacja wielowymiarowych danych - aplikacja webowa
Aplikacja napisana przy użyciu Django 2.1.7 oraz Python 3.6 posiadająca system rejestracji oraz logowania, a także możliwość uruchomienia aplikacji MPI.

## Instalacja - Docker
Do działania aplikacji jest niezbędny docker.
Żeby go zainstalować, należy wykonać poniższe polecenia

```
$ sudo apt-get update

$ sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
    
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

$ sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
   
$ sudo apt-get update

$ sudo apt-get install docker-ce docker-ce-cli containerd.io
```

## Uruchomienie - Docker
```
$ git clone https://github.com/Michal-Madarasz/aiirProject.git

$ cd aiirProject

$ docker build -t django_mpi .

$ docker run -p 8000:8000 -d django_mpi
```

Po wykonaniu komend aplikacja powinna być dostępna pod adresem:
http://localhost:8000

## Uruchomienie - Docker compose
```
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

$ sudo chmod +x /usr/local/bin/docker-compose

$ docker-compose --version
```
