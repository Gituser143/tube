tube
====

A video sharing platform made with django!

Installation
------------

### Get code from repository

```sh
git clone https://github.com/Gituser143/tube.git
cd tube
```

### Install Python Dependencies:

```sh
pip3 install -r requirements.txt
```

### External Dependencies:

Debian based systems:

```sh
sudo apt install ffmpeg
```

Mac:

```sh
brew install ffmpeg
```

From source, refer to instructions [here](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg)

Running the application
-----------------------

Navigate to `oyt_python` and Migrate only for the first time!

```sh
cd oyt_python
python3 manage.py migrate
```

To start the server, run:

```sh
python3 manage.py runserver
```

Navigate to `localhost:8000` to access the application!
