# Flack Server

Chat server designed as a back end counterpart to [this Android client](https://github.com/skomaromi/flack-client-android).



## Getting started

*Inspired by Coding For Entrepreneurs' Rapid-ChatXChannels start [guide](https://github.com/codingforentrepreneurs/Rapid-ChatXChannels/blob/master/README.md). Steps provided are written from an Ubuntu (18.10) perspective. Should work on other Debian-based Linux distributions as well. Windows and macOS users should not try to follow this blindly.*

1. Install dependencies.
```bash
$ sudo apt install virtualenv python3-dev build-essential curl redis-server
```

2. [Install NodeJS.](https://github.com/nodesource/distributions/blob/master/README.md#installation-instructions)

3. [Install IPFS and start it.](https://github.com/ipfs-shipyard/ipfs-desktop#install)


Now, assuming you're in the main repository directory (`ls` output includes `run-server.sh`), you need to do the following:

1. Create a virtual environment.
```bash
$ virtualenv -p python3 .
```

2. Enter (activate) it.
```bash
$ source bin/activate
```

3. Once in there, install all the dependencies it might need.
```bash
(flack-server) $ pip install -r requirements.txt
```

4. Still in virtual environment, create an administrator user.
```bash
(flack-server) $ cd src
(flack-server) $ python manage.py migrate
(flack-server) $ python manage.py createsuperuser
```

5. Done!



## Run

1. Make sure IPFS daemon is running.
2. Execute `run-server.sh`.



## Next steps

Now that your server is up and running, you can:

* play around with the built-in web interface at `localhost:8000`,
* use the [Android client](https://github.com/skomaromi/flack-client-android) or
* roll your own solution ([documentation](DOCS.md) might help here).

