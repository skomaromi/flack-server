# Flack Server

## Install
*Inspired by Coding For Entrepreneurs' Rapid-ChatXChannels start [guide](https://github.com/codingforentrepreneurs/Rapid-ChatXChannels/blob/master/README.md)*

1. install all sorts of stuff we will need for this
```bash
$ sudo apt install virtualenv python3-dev build-essential curl redis-server
```

2. [install NodeJS](https://github.com/nodesource/distributions/blob/master/README.md#installation-instructions)

3. [install IPFS and start it](https://github.com/ipfs-shipyard/ipfs-desktop#install)


Now, assuming you're in the repository directory (`ls` gives you files like `run-server.sh`), you need to do the following:

1. create a virtual environment
```bash
virtualenv -p python3 .
```

2. enter (er, activate) it
```bash
$ source bin/activate
```

3. once in there, install all the funny dependencies it might need
```bash
$ pip install -r requirements.txt
```

4. still in venv, create an admin user
```bash
$ cd src
$ python manage.py migrate
$ python manage.py createsuperuser
```

5. done!

## Run
1. make sure IPFS daemon is running
2. execute `run-server.sh`
