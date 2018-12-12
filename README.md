This is *Piccolo 2 Web* by [Livia Jakob](https://bitbucket.org/liviaj/). It provides a graphical web interface for the Piccolo optical spectroradiometer. There are several related repositories: piccolo2-server, piccolo2-common and piccolo2-client.


## Installation guide for the piccolo2 web GUI:
**Required repositories:** piccolo2-common, piccolo2-client, piccolo2-web

1. Create virtual environment with **miniconda** and install dependencies
```
>>> cd piccolo2-web
>>> conda env create -f piccolo2.yml
>>> source activate piccolo2
```

2. Set up common (within piccolo2-common)
```
>>> python setup.py install
```

3. Set up client (within piccolo2-client)
```
>>> python setup.py install
```
4. Set up web (within piccolo2-web)
```
>>> pip install -r requirements.txt
>>> python setup.py install
```

Run webapp:
```
>>> piccolo2-web -u http://piccolo8:8080
```
Run webapp with development server:
```
>>> piccolo2-web -u http://piccolo-dev:8080
```