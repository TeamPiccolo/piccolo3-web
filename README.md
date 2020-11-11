This is *Piccolo 3 Web* originally written by [Livia Jakob](https://github.com/liviajakob). It provides a graphical web interface for the Piccolo optical spectroradiometer. There are several related repositories: piccolo3-server, piccolo3-common and piccolo3-client.


## Installation guide for the piccolo3 web GUI:
**Required repositories:** piccolo3-common, piccolo3-client, piccolo3-web

Create virtual environment with **miniconda** and install dependencies
```
>>> cd piccolo3-web
>>> conda env create -f piccolo3.yml
>>> source activate piccolo3
```

Set up common (within piccolo3-common)
```
>>> python setup.py install
```

Set up client (within piccolo3-client)
```
>>> python setup.py install
```
Set up web (within piccolo3-web)
```
>>> pip install -r requirements.txt
>>> python setup.py install
```

Run webapp:
```
>>> PICCOLO=coap://piccolo-thing2 uvicorn piccolo3.app:app --host 0.0.0.0 --port 8000 --loop asyncio   --reload
```
