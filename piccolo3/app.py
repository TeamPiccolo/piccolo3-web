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

import argparse, os
from piccolo3 import client as piccolo
from quart import Quart, render_template, jsonify

app = Quart(__name__)

try:
    baseurl = os.environ['PICCOLO']
except:
    baseurl = 'coap://localhost'

psys = piccolo.PiccoloSysinfo(baseurl)
pctrl = piccolo.PiccoloControl(baseurl)
pdata = piccolo.PiccoloDataDir(baseurl)

@app.route('/info',methods=['GET'])
async def info():
    '''get json info'''
    info = await psys.get_info()
    info['status'] = await pctrl.get_status()
    if info['status'] == 'idle':
        info['state']  = 'green'
    else:
        info['state'] = 'orange'
    return jsonify(info)

@app.route('/', methods=['GET'])
async def index():
    '''HTML for index page of the dashboard'''
    info = await psys.get_info()
    extra_info = {}
    extra_info['datadir'] = await pdata.get_datadir()
    extra_info['host'] = await psys.get_host()
    extra_info['server_version'] = await psys.get_server_version()
    extra_info['client_version'] = piccolo.__version__
    return await render_template('index.html',**info, **extra_info)

