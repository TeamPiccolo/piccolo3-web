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
import datetime,pytz
from piccolo3 import client as piccolo
from piccolo3.common import PiccoloSpectraList
from quart import Quart, render_template, jsonify,request, websocket, copy_current_websocket_context, redirect
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

    if not await pclient.sys.isConnected():
        app.logger.warning('waiting for piccolo server')
        await asyncio.sleep(1)
        return redirect(request.url)
    
    info = await pclient.sys.get_info()
    info['clock'] = await pclient.sys.get_clock()
    info['dt'] = datetime.datetime.now()
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
pdata_ws = PiccoloWebsocket(pclient.data.register_callback)
pscheduler_ws = PiccoloWebsocket(pclient.scheduler.register_callback)
@app.websocket('/piccolo')
@piccolo_ws
@pdata_ws
@pscheduler_ws
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
        app.logger.info('received piccolo_ws {}({})'.format(cmd,args))
        if cmd == 'current_run':
            try:
                await pclient.data.set_current_run(args)
            except Exception as e:
                app.logger.error(str(e))
                continue
        elif cmd == 'numSequences':
            try:
                await pclient.control.set_numSequences(args)
            except Exception as e:
                app.logger.error(str(e))
                continue
        elif cmd == 'autointegration':
            try:
                await pclient.control.set_autointegration(args)
            except Exception as e:
                app.logger.error(str(e))
                continue
        elif cmd == 'delay':
            try:
                await pclient.control.set_delay(args)
            except Exception as e:
                app.logger.error(str(e))
                continue
        elif cmd == 'target':
            try:
                await pclient.control.set_target(args)
            except Exception as e:
                app.logger.error(str(e))
                continue
        elif cmd == 'record':
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
        elif cmd == 'auto':
            try:
                await pclient.control.auto()
            except Exception as e:
                app.logger.error(str(e))
                continue
        elif cmd == 'pause':
            try:
                await pclient.control.pause()
            except Exception as e:
                app.logger.error(str(e))
                continue
        elif cmd == 'abort':
            try:
                await pclient.control.abort()
            except Exception as e:
                app.logger.error(str(e))
                continue
        elif cmd == 'sync':
            try:
                await pclient.sys.set_clock(args['time'])
            except Exception as e:
                app.logger.error(str(e))
            ptime = await pclient.sys.get_clock()
            await websocket.send(json.dumps({'timeChanged':ptime}))
            continue
        elif cmd == 'quietTimeEnabled':
            try:
                await pclient.scheduler.set_quietTimeEnabled(args)
            except Exception as e:
                app.logger.error(str(e))
            continue
        elif cmd == 'quietTimeStart':
            t = datetime.time(*args).replace(tzinfo=pytz.utc)
            try:
                await pclient.scheduler.set_quietStart(t)
            except Exception as e:
                app.logger.error(str(e))
            continue
        elif cmd == 'quietTimeEnd':
            t = datetime.time(*args).replace(tzinfo=pytz.utc)
            try:
                await pclient.scheduler.set_quietEnd(t)
            except Exception as e:
                app.logger.error(str(e))
            continue
        elif cmd == 'suspend_job':
            try:
                await pclient.scheduler.suspend(args)
            except Exception as e:
                app.logger.error(str(e))
            continue
        elif cmd == 'unsuspend_job':
            try:
                await pclient.scheduler.unsuspend(args)
            except Exception as e:
                app.logger.error(str(e))
            continue
        elif cmd == 'delete_job':
            try:
                await pclient.scheduler.delete(args)
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
        for k in ['min_time','max_time','status']:
            v = await pclient.spec[spec].a_get(k)
            await websocket.send(json.dumps((spec,k,v)))
        for c in channels:
            for m in ['current_time','autointegration']:
                k = m+'/'+c
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
    dt = datetime.datetime.now()
    channels = await pclient.spec.get_channels()
    spectrometers = await pclient.spec.get_spectrometers()
    current_run = await pclient.data.get_current_run()
    numSequences = await pclient.control.get_numSequences()
    auto = await pclient.control.get_autointegration()
    delay = await pclient.control.get_delay()
    target = await pclient.control.get_target()
    return await render_template('record.html', 
                                 clock = clock,
                                 dt = dt,
                                 channels=channels,
                                 spectrometers = spectrometers,
                                 current_run = current_run,
                                 numSequences = numSequences,
                                 auto = auto,
                                 delay = delay,
                                 target = target )

@app.route('/scheduler', methods=['GET'])
async def scheduler():
    '''Renders HTML for scheduler page'''
    clock = await pclient.sys.get_clock()
    dt = datetime.datetime.now()
    current_run = await pclient.data.get_current_run()
    numSequences = await pclient.control.get_numSequences()
    auto = await pclient.control.get_autointegration()
    delay = await pclient.control.get_delay()
    target = await pclient.control.get_target()
    qtEnabled = await pclient.scheduler.get_quietTimeEnabled()
    qtStart = await pclient.scheduler.get_quietStart()
    qtEnd = await pclient.scheduler.get_quietEnd()
    
    return await render_template('scheduler.html', 
                                 clock = clock,
                                 dt = dt,
                                 current_run = current_run,
                                 numSequences = numSequences,
                                 auto = auto,
                                 delay = delay,
                                 target = target,
                                 qtEnabled = qtEnabled,
                                 qtStart = qtStart,
                                 qtEnd = qtEnd )

@app.route('/results',methods=['GET'])
async def results():
    '''Renders HTML for results page'''

    runList = await pclient.data.get_runs()
    currentRun = await pclient.data.get_current_run()
    spectraList = await currentRun.get_spectra_list()

    return await render_template('results.html',runList=runList,
                                 currentRun = currentRun.name,
                                 spectraList = spectraList)


temperature_ws = PiccoloWebsocket(pclient.spec.register_callback)
@app.websocket('/tempctrl')
@temperature_ws
async def tempctrl():
    for spec in pclient.spec.keys():
        k = 'status'
        v = await pclient.spec[spec].a_get(k)
        await websocket.send(json.dumps((spec,k,v)))
        if pclient.spec[spec].haveTEC:
            await websocket.send(json.dumps((spec,'present',True)))
            ct = await pclient.spec[spec].current_temperature()
            await websocket.send(json.dumps((spec,'current',ct)))
            t = await pclient.spec[spec].get_target_temperature()
            await websocket.send(json.dumps((spec,'target',t)))
            e = await pclient.spec[spec].get_TECenabled()
            await websocket.send(json.dumps((spec,'enabled',e)))
        else:
            await websocket.send(json.dumps((spec,'present',False)))

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
        if spec not in pclient.spec:
            error = 'no such spectrometer %s'%spec
            app.logger.error(error)
            continue
        if key == 'target':
            try:
                await pclient.spec[spec].set_target_temperature(value)
            except Exception as e:
                # log error and restore current value
                error = str(e)
                app.logger.error(error)
                t = await pclient.spec[spec].get_target_temperature()
                await websocket.send(json.dumps((spec,'target',t)))
                continue
        elif key == 'enabled':
            try:
                await pclient.spec[spec].set_TECenabled(value)
            except Exception as e:
                # log error and restore current value
                error = str(e)
                app.logger.error(error)
                e = await pclient.spec[spec].get_TECenabled()
                await websocket.send(json.dumps((spec,'enabled',e)))
        else:
            app.logger.error('unknown key: {}'.format(key))

@app.route('/ctemp',methods=['GET'])
async def ctemp():
    '''get the current temperature'''
    temp = {}
    for spec in pclient.spec.keys():
        temp[spec] = await pclient.spec[spec].current_temperature()
    return jsonify(temp)
        
@app.route('/temperature',methods=['GET'])
async def temperature():
    '''Renders HTML for temperature page'''
    clock = await pclient.sys.get_clock()
    dt = datetime.datetime.now()
    spectrometers = await pclient.spec.get_spectrometers()
    
    return await render_template('temperature.html',
                                 clock = clock,
                                 dt = dt,
                                 spectrometers = spectrometers
    )

@app.route('/jobs',methods=['GET'])
async def jobs():
    """get list of scheduled jobs"""

    jobs = await pclient.scheduler.get_jobs()
    return jsonify(jobs)

@app.route('/data',methods=['GET'])
async def get_runs():
    '''return list of runs'''

    current_run = request.args.get('current',default=0,type=int)

    if current_run == 1:
        data = await pclient.data.get_current_run()
        data = data.name
    else:
        data = await pclient.data.get_runs()

    return jsonify(data)

@app.route('/data/<run>',methods=['GET'])
async def get_run(run):
    '''return list of spectra'''

    if run not in pclient.data:
        raise APIRequestException('no such run %s'%run)

    data = await pclient.data[run].get_spectra_list()

    return jsonify(data)

@app.route('/data/<run>/<spectra>',methods=['GET'])
async def get_spectra(run,spectra):
    '''return list of spectra'''

    data_type = request.args.get('data',default='raw')
    
    if run not in pclient.data:
        raise APIRequestException('no such run %s'%run)
    
    spectra = await pclient.data[run].get_spectra(spectra)

    if data_type == 'raw':
        return spectra
    else:
        spectra = PiccoloSpectraList(data=spectra)
        if data_type.startswith('plot_'):
            d = data_type[5:]
            if d == 'all':
                directions = spectra.directions
            else:
                directions = [d]
            data = []
            for d in directions:
                for s in ['Dark','Light']:
                    for spec in spectra.getSpectra(d,s):
                        xy = []
                        p = spec.pixels
                        w = spec.waveLengths
                        for i in range(len(p)):
                            xy.append({'x':int(w[i]),'y':int(p[i])})
                        sDict = spec.as_dict(pixelType='list')
                        sDict['plotList'] = xy
                        sDict['Directions'] = spectra.directions
                        data.append(sDict)
            return jsonify(data)
        
    raise APIRequestException('unknown request %s'%data_type)

class APIRequestException(Exception):
    '''Exception class for API Exceptions
    
    Inherits from Exceptions    
    
    Use:
        raise APIRequestException('Error message', status_code=XXX)
    
    '''
    
    def __init__(self, message, status_code=400):
        '''
        Input Parameters:
            message (str) - Error message
            status_code (int) - (optional) status code of the occurred error
        
        '''
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        '''Converts the error message to a dictionnary
        
        Returns:
            dict - a dictionnary of the Error
        '''
        rv = dict(())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv


@app.errorhandler(APIRequestException)
def handle_apiRequestException(error):
    '''error handler to handle the APIRequestException
    
    Response:
        a JSON with information about the occurred Error
    '''
    response = error.to_dict()
    response = jsonify(response)
    return response



if __name__ == '__main__':
    import uvicorn

    uvicorn.run("app:app",host='0.0.0.0',port=8000,log_level='info',loop='asyncio',debug=True,workers=1,reload=False)
