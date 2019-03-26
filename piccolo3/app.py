#!/usr/bin/env python

# Copyright 2018 The Piccolo Team
#
# This file is part of piccolo3-web.
#
# piccolo3-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo3-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo3-web.  If not, see <http://www.gnu.org/licenses/>.

'''
Web GUI

App Endpoints:
    index - renders the home page
    results - renders the result page
    
    info - returns status infos



'''

import argparse, os, json
from piccolo3 import client as piccolo
from quart import Quart, render_template, jsonify,request, websocket, copy_current_websocket_context
from functools import wraps
import asyncio

app = Quart(__name__)

try:
    baseurl = os.environ['PICCOLO']
except:
    baseurl = 'coap://localhost'

psys = piccolo.PiccoloSysinfo(baseurl)
pctrl = piccolo.PiccoloControl(baseurl)
pdata = piccolo.PiccoloDataDir(baseurl)
pspec = piccolo.PiccoloSpectrometers(baseurl)

async def get_info(sysinfo=True):
    if sysinfo:
        info = await psys.get_info()
    else:
        info = {}
    info['clock'] = await psys.get_clock()
    info['status'] = await pctrl.get_status()
    if info['status'] == 'idle':
        info['state']  = 'green'
    else:
        info['state'] = 'orange'
    return info

@app.route('/info',methods=['GET'])
async def info():
    '''get json info'''
    sysinfo = request.args.get('sysinfo',default=1,type=int)
    info = await get_info(sysinfo==1)
    return jsonify(info)

@app.route('/', methods=['GET'])
async def index():
    '''HTML for index page of the dashboard'''
    info = await get_info(True)
    extra_info = {}
    extra_info['datadir'] = await pdata.get_datadir()
    extra_info['host'] = await psys.get_host()
    extra_info['server_version'] = await psys.get_server_version()
    extra_info['client_version'] = piccolo.__version__
    return await render_template('index.html',**info, **extra_info)

spectrometer_connected = set()
def collect_spectrometer_ws(func):
    @wraps(func)
    async def wrapper(*args,**kwargs):
        global spectrometer_connected
        spectrometer_connected.add(websocket._get_current_object())
        try:
            return await func(*args,**kwargs)
        finally:
            spectrometer_connected.remove(websocket._get_current_object())
    return wrapper

async def spectrometer_changed(message):
    for ws in spectrometer_connected:
        await ws.send(message)

pspec.register_callback(spectrometer_changed)

@app.websocket('/spectrometers')
@collect_spectrometer_ws
async def spectrometers():
    channels = await pspec.get_channels()
    for spec in pspec.keys():
        for k in ['min_time','max_time']:
            v = await pspec[spec].a_get(k)
            await websocket.send(json.dumps((spec,k,v)))
        for c in channels:
            k = 'current_time/'+c
            v = await pspec[spec].a_get(k)
            await websocket.send(json.dumps((spec,k,v)))
    while True:
        msg = await websocket.receive()
        try:
            d = json.loads(msg)
            spec = d[0]
            key = d[1]
            value = d[2]
        except:
            error = 'could not parse message %s'%msg
            app.logger.error(error)
            continue
        app.logger.info('received spectrometer_ws: %s'%msg)
        if spec not in pspec:
            error = 'no such spectrometer %s'%spec
            app.logger.error(error)
            continue
        try:
            await pspec[spec].a_put(key,value)
        except Exception as e:
            # log error and restore current value
            error = str(e)
            app.logger.error(error)
            v = await pspec[spec].a_get(key)
            await websocket.send(json.dumps((spec,key,v)))
            continue
        
@app.route('/record', methods=['GET'])
async def record():
    '''Renders HTML for record page'''
    info = await get_info(False)
    channels = await pspec.get_channels()
    spectrometers = await pspec.get_spectrometers()
    return await render_template('record.html', **info, channels=channels, spectrometers = spectrometers)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("app:app",host='0.0.0.0',port=8000,log_level='info',loop='asyncio',debug=True,workers=1,reload=False)
