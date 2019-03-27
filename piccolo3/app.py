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


pclient = piccolo.PiccoloSystem(baseurl)

@app.route('/info',methods=['GET'])
async def info():
    '''get json info'''
    info = await pclient.sys.get_info()
    return jsonify(info)

@app.route('/', methods=['GET'])
async def index():
    '''HTML for index page of the dashboard'''
    info = await pclient.sys.get_info()
    info['clock'] = await pclient.sys.get_clock()
    info['datadir'] = await pclient.data.get_datadir()
    info['host'] = await pclient.sys.get_host()
    info['server_version'] = await pclient.sys.get_server_version()
    info['client_version'] = piccolo.__version__
    return await render_template('index.html',**info)

class PiccoloWebsocket:
    def __init__(self,cb):
        self._connected_ws = set()
        # register callback
        cb(self.update)

    def __call__(self,func):
        @wraps(func)
        async def wrapper(*args,**kwargs):
            self._connected_ws.add(websocket._get_current_object())
            try:
                return await func(*args,**kwargs)
            finally:
                self._connected_ws.remove(websocket._get_current_object())
        return wrapper
        
    async def update(self,message):
        for ws in self._connected_ws:
            await ws.send(message)

piccolo_ws = PiccoloWebsocket(pclient.control.register_callback)
@app.websocket('/piccolo')
@piccolo_ws
async def piccolo_ctrl():
    s = await pclient.control.get_status()
    await websocket.send(json.dumps({'status':s}))
    while True:
        msg = await websocket.receive()
        try:
            cmd,args = json.loads(msg)
        except:
            error = 'could not parse message %s'%msg
            app.logger.error(error)
            continue
        app.logger.info('received piccolo_ws %s'%msg)
        if cmd == 'record':
            try:
                await pclient.control.record_sequence(**args)
            except Exception as e:
                app.logger.error(str(e))
                continue
        elif cmd == 'dark':
            try:
                await pclient.control.record_dark(**args)
            except Exception as e:
                app.logger.error(str(e))
                continue
        else:
            app.logger.error('unkown command %s'%msg)

        
spectrometer_ws = PiccoloWebsocket(pclient.spec.register_callback)
@app.websocket('/spectrometers')
@spectrometer_ws
async def spectrometers():
    channels = await pclient.spec.get_channels()
    for spec in pclient.spec.keys():
        for k in ['min_time','max_time']:
            v = await pclient.spec[spec].a_get(k)
            await websocket.send(json.dumps((spec,k,v)))
        for c in channels:
            k = 'current_time/'+c
            v = await pclient.spec[spec].a_get(k)
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
        if spec not in pclient.spec:
            error = 'no such spectrometer %s'%spec
            app.logger.error(error)
            continue
        try:
            await pclient.spec[spec].a_put(key,value)
        except Exception as e:
            # log error and restore current value
            error = str(e)
            app.logger.error(error)
            v = await pclient.spec[spec].a_get(key)
            await websocket.send(json.dumps((spec,key,v)))
            continue
        
@app.route('/record', methods=['GET'])
async def record():
    '''Renders HTML for record page'''
    clock = await pclient.sys.get_clock()
    channels = await pclient.spec.get_channels()
    spectrometers = await pclient.spec.get_spectrometers()
    current_run = await pclient.data.get_current_run()
    return await render_template('record.html', 
                                 clock = clock,
                                 channels=channels,
                                 spectrometers = spectrometers,
                                 current_run = current_run)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("app:app",host='0.0.0.0',port=8000,log_level='info',loop='asyncio',debug=True,workers=1,reload=False)
