This is *Piccolo 3 Web* originally written by [Livia Jakob](https://github.com/liviajakob). It provides a graphical web interface for the Piccolo optical spectroradiometer. There are several related repositories: piccolo3-server, piccolo3-common and piccolo3-client.


## Installation guide for the piccolo3 web GUI:
**Required repositories:** piccolo3-common, piccolo3-client, piccolo3-web

Install piccolo3-common and piccolo3-client first.

Set up web (within piccolo3-web):

If you use a Debian-based Linux system, you can install requirements by
```
sudo apt install python3-numpy python3-quart python3-tz python3-configobj python3-uvicorn python3-jinja2
```
If you use miniconda and have created a virtual environment, make sure it is active.
Finally, install the package with
```
python setup.py install
```
Running the setup also installs any missing dependencies.

## Run web app
Run the web app by
```
PICCOLO=coap://piccolo-thing2 uvicorn piccolo3.app:app --host 0.0.0.0 --port 8000 --loop asyncio --reload
```
where `piccolo-thing2` needs to be replaced with the name or IP address of the Raspberry Pi on which the Piccolo server is running. If you run the web app on the same computer, you can use 127.0.0.1 (localhost). To use the app, point your browser to the computer on which the web app is running, port 8000, for example `http://192.168.1.5:8000` if the IP is 192.168.1.5.
