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

import web
import argparse
import logging

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

    
    log = logging.getLogger("piccolo")
    if args.debug:
        log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(name)s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    
    if args.xbee_address != None:
        connection = ('xbee',args.xbee_address)
    else:
        connection = ('http',args.piccolo_url)

    #player.main(connection)
    

if __name__ == '__main__':
    main()
