#!/usr/bin/env python

# Copyright 2018 The Piccolo Team
#
# This file is part of piccolo2-web.
#
# piccolo2-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo2-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo2-web.  If not, see <http://www.gnu.org/licenses/>.

'''
Web GUI

App Endpoints:
    index - renders the home page
    results - renders the result page
    
    info - returns status infos



'''


import web
import argparse
import logging
from flask import Flask, render_template, jsonify
from definitions import CONFIG_PATH
from configobj import ConfigObj

# global variable of connection settings
piccoloProxy= None


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u','--piccolo-url',metavar='URL',default='http://localhost:8080',help='set the URL of the piccolo server, default http://localhost:8080')
    group.add_argument('-x','--xbee-address',metavar='ADR',help="the address of the xbee radio")
    parser.add_argument('-d','--debug', action='store_true',default=False,help="enable debugging output")
    parser.add_argument('-v','--version',action='store_true',default=False,help="print version and exit")
    
    args = parser.parse_args()

    if args.version:
        from client import __version__
        print 'client:',__version__
        print 'web:',web.__version__
        return

    # logger
    log = logging.getLogger("piccolo")
    if args.debug:
        log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(name)s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    
    # this doesn't do anything at the moment
    if args.xbee_address != None:
        connection = ('xbee',args.xbee_address)
    else:
        connection = ('http',args.piccolo_url)

    global piccoloProxy
    piccoloProxy=web.main(connection)
    print(piccoloProxy.piccoloInfo)
    run(debug=args.debug)
    
    
def run(debug):
    config = ConfigObj(CONFIG_PATH)
    params={'debug': debug, 'threaded': True}
    params['host'] = config['web']['host']
    try:
        params['port']= config['web']['port']
    except:
        pass
    app.run(**params)

app = Flask(__name__)
   

@app.route('/', methods=['GET'])
def index():
    '''HTML for index page of the dashboard'''
    info = piccoloProxy.piccoloInfo
    return render_template('index.html', **info)


@app.route('/results', methods=['GET'])
def results():
    '''Renders HTML for result page'''
    info = piccoloProxy.piccoloInfo
    return render_template('results.html', **info)
    

@app.route('/info', methods=['GET'])
def info():
    '''Returns info of the clients status as JSON
    
    '''
    info = piccoloProxy.piccoloInfo
    return jsonify(info)
    



## Error Handling

class APIRequestException(Exception):
    '''Exception class for API Exceptions
    
    Inherits from Exceptions    
    
    Use:
        raise APIRequestException('Error message', status_code=XXX)
    
    '''
    
    # default status code is 400
    status_code = 400

    def __init__(self, message, status_code=None):
        '''
        Input Parameters:
            message (str) - Error message
            status_code (int) - (optional) status code of the occurred error
        
        '''
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        '''Converts the error message to a dictionnary
        
        Returns:
            dict - a dictionnary of the Error
        '''
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv


@app.errorhandler(APIRequestException)
def handle_apiRequestException(error):
    '''Flask error handler to handle the APIRequestException
    
    Response:
        a JSON with information about the occurred Error
    '''
    response = error.to_dict()
    response = jsonify(response)
    return response







if __name__ == '__main__':
    main()
    
