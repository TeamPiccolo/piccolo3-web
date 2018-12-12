# Copyright 2014-2016 The Piccolo Team
#
# This file is part of piccolo2-player.
#
# piccolo2-player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo2-player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo2-player.  If not, see <http://www.gnu.org/licenses/>.

__all__ = ['main']

import piccolo2.client
import threading
from piccolo2.common import PiccoloExtendedStatus
from piccolo2.web import __version__ as version

#import player_ui
#import connect_ui
#from ScheduleList import *
#from Schedule import ScheduleDialog
#from QuietTime import QuietTimeDialog
#from RunList import RunListDialog
#from SpectraList import SpectraListDialog
#import datetime,pytz

TIMEFORMAT = "%Y-%m-%dT%H:%M:%S"

class IntegrationTimes():
    def __init__(self):
        self._shutters = None
        self._spectrometers = None
        self._piccolo = None
        self._listenerID = None
        self._updatePiccolo = True

        #self.itemChanged.connect(self.updateIntegrationTime)

    
    @property
    def shutters(self):
        return self._shutters
    
    @property
    def spectrometers(self):
        return self._spectrometers
    
    
    
    def updateIntegrationTime(self, column, row, value):
        '''Updates an integration time value
        
        :param column: column of the value that should be updated
        :param row: row of the value that should be updated
        :param value: new value
        
        '''
        try:
            data = float(value)
        except:
            #TODO: handle case with Exception
            return
        if self._updatePiccolo:
            shutter = self._shutters[column]
            spectrometer = self._spectrometers[row]
            if shutter == 'min':
                self._piccolo.setMinIntegrationTime(spectrometer=spectrometer,milliseconds=data)
            elif shutter == 'max':
                self._piccolo.setMaxIntegrationTime(spectrometer=spectrometer,milliseconds=data)
            else:
                self._piccolo.setIntegrationTime(shutter=shutter,
                                                 spectrometer=spectrometer,
                                                 milliseconds=data)


    def getIntegrationTime(self,spectrometer,shutter):
        #j = self._spectrometers.index(spectrometer)
        #i = self._shutters.index(shutter)
        #source = 0
        if shutter == 'min':
            data = self._piccolo.getMinIntegrationTime(spectrometer=spectrometer)
        elif shutter == 'max':
            data = self._piccolo.getMaxIntegrationTime(spectrometer=spectrometer)
        else:
            data = int(self._piccolo.getIntegrationTime(shutter=shutter, spectrometer=spectrometer))
            #source = self._piccolo.getIntegrationTimeSource(shutter=shutter,spectrometer=spectrometer)
        #self._updatePiccolo = False
        #item = QtGui.QStandardItem(str(data))
        #if source == 0:
            #item.setForeground(QtGui.QBrush(QtGui.QColor('black')))
        #elif source == 1:
            #item.setForeground(QtGui.QBrush(QtGui.QColor('green')))
        #elif source == 2:
            #item.setForeground(QtGui.QBrush(QtGui.QColor('blue')))
        #self.setItem(j,i,item)
        #self._updatePiccolo = True
        return data
            
    def piccoloConnect(self,piccolo):
        self._piccolo = piccolo
        self._shutters = ['min']+self._piccolo.getShutterList()+['max']
        self._spectrometers = self._piccolo.getSpectrometerList()

        #self.setRowCount(len(self._spectrometers))
        #self.setColumnCount(len(self._shutters))

        #for i in range(len(self._shutters)):
            #self.setHorizontalHeaderItem(i,QtGui.QStandardItem(self._shutters[i]))
        #for j in range(len(self._spectrometers)):
            #self.setVerticalHeaderItem(j,QtGui.QStandardItem(self._spectrometers[j]))


    def getIntegrationTimes(self):
        integrationTimes = {}
        integrationTimes['shutters'] = self._shutters
        integrationTimes['spectrometers'] = self._spectrometers
        integrationTimes['values'] = []
        for spectrometer in self._spectrometers:
            col = []
            for shutter in self._shutters:
                val = self.getIntegrationTime(spectrometer,shutter)
                col.append(val)
            integrationTimes['values'].append(col)
        return integrationTimes
        


'''class ConnectDialog():
    def __init__(self):
        #super(ConnectDialog, self).__init__(parent)
        #self.setupUi(self)
        pass

    def setConnection(self,connection,data):
        if connection == 'http':
            self.connectHTTP.setChecked(True)
            self.serverURL.setText(data)
        elif connection == 'xbee':
            self.connectXBee.setChecked(True)
            self.xbeeSerial.setText(data)
        else:
            raise RuntimeError, 'unkown connection type',connection

    @property
    def getConnectionMethod(self):
        if self.connectHTTP.isChecked():
            return 'http'
        elif self.connectXBee.isChecked():
            return 'xbee'
        else:
            raise RuntimeError, 'Unkown connection method'

    def getData(self,parent=None):
        dialog = ConnectDialog(parent=parent)
        result = self.exec_()

        if result != QtGui.QDialog.Accepted:
            return

        method = self.getConnectionMethod
        data = None
        if method == 'http':
            data = self.serverURL.text()
        elif method == 'xbee':
            data = self.xbeeSerial.text()
        return method,str(data)'''


class WebApp():
    def __init__(self):

        # the piccolo connection
        self._piccolo = None
        self._connectionType = 'http'
        self._connectionData = 'http://localhost:8080'

        # dictionary to store info such as directory, versions
        self._piccoloInfo = {}

        # the extended status
        self._extendedStatus = None

        # version numbers
        self._piccoloInfo['clientVersion'] = piccolo2.client.__version__
        self._piccoloInfo['webAppVersion'] = version
        
        # status buttons
        #self.syncTimeButton.clicked.connect(self.syncTime)

        # the integration times
        self._times = IntegrationTimes()
        #self.integrationTimeView.setModel(self._times)

        # connect recording buttons
        #self.startRecordingButton.clicked.connect(self.startRecording)
        #self.stopRecordingButton.clicked.connect(self.stopRecording)
        #self.autoButton.clicked.connect(self.autoIntegrate)
        #self.darkButton.clicked.connect(self.recordDark)
        #self.pauseRecordingButton.clicked.connect(self.pauseRecording)

        #self.selectRunButton.clicked.connect(self.setRun)
        
        # connect spectra load boxes
        self._spectraList = []
        self._runList = []
        self._updateSpectraFile = True
        self._spectra = None
        self._selectedDirection = None
        self._selectedSpectrum = None
        #self.selectSpectrumButton.clicked.connect(self.downloadSpectra)
        #self.selectShutter.currentIndexChanged.connect(self.setSpectrumAndDirection)
        #self.selectSpectrum.currentIndexChanged.connect(self.setSpectrumAndDirection)

        # hook up scheduler
        #self._scheduledJobs = PiccoloSchedule()
        #self._scheduledJobsDialog = ScheduleListDialog(scheduledJobs = self._scheduledJobs)

        # hook up menu
        #self.action_Connect.triggered.connect(self.connectDialog)
        #self.actionSave_Plot.triggered.connect(self.savePlot)
        #self.action_Quit.triggered.connect(QtGui.qApp.quit)
        #self.action_Add_Schedule.triggered.connect(self.addSchedule)
        #self.actionList_Schedules.triggered.connect(self.scheduledJobsDialog)
        #self.actionQuietTime.triggered.connect(self.quietTimeDialog)

        # hook up autointegration
        #self.checkAutoIntegrate.stateChanged.connect(self.changeAutoIntegrationRepeats)
        #self.autoIntegrateRepeat.editingFinished.connect(self.changeAutoIntegrationRepeats)
        #self.auto = None

        # hook up number of measurements per run
        #self.repeatMeasurements.editingFinished.connect(self.changeNCycles)
        self.nCycles = None

        # hook up delay between measurements
        #self.delayMeasurements.editingFinished.connect(self.changeDelay)
        self.delay = None

        # hook up current run
        #self.outputDir.editingFinished.connect(self.changeCurrentRun)
        #self.currentRun = None
        
        # periodically check status
        #self.statusLabel = QtGui.QLabel()
        #self.statusbar.addWidget(self.statusLabel)
        #self.timer = QtCore.QTimer()
        
        
        
        #self.timer.timeout.connect(self.status)
        # check every second
        #self.timer.start(1000)

        
    '''def closeEvent(self,event):
        if self._piccolo is not None:
            self._piccolo.disconnect()
        
    def syncTime(self):
        now = datetime.datetime.now(tz=pytz.utc)
        self._piccolo.piccolo.setClock(clock=now.isoformat())'''

    '''def disableEdit(self):
        #self.integrationTimeView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        # current run
        self.checkAutoIntegrate.setEnabled(False)
        self.autoIntegrateRepeat.setEnabled(False)
        self.repeatMeasurements.setEnabled(False)
        self.delayMeasurements.setEnabled(False)
        self.autoIntegrateTimeout.setEnabled(False)
        self.outputDir.setEnabled(False)

    def enableEdit(self):
        #self.integrationTimeView.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.checkAutoIntegrate.setEnabled(True)
        if self.checkAutoIntegrate.checkState() == 2:
            self.autoIntegrateRepeat.setEnabled(True)
        else:
            self.autoIntegrateRepeat.setEnabled(False)
        self.repeatMeasurements.setEnabled(True)
        self.delayMeasurements.setEnabled(True)
        self.autoIntegrateTimeout.setEnabled(True)
        self.outputDir.setEnabled(True)'''
        

    '''def startRecording(self,start=None,end=None,interval=None):
        #n = self.repeatMeasurements.value()
        #if n==0:
        #    n='Inf'
        kwds ={}
        kwds['timeout'] = self.autoIntegrateTimeout.value()
        if start not in [None, False]:
            kwds['at_time'] = start
            # get parameters from current state
            kwds['delay'] = self.delay
            kwds['nCycles'] = self.nCycles
            kwds['auto'] = self.auto
            kwds['currentRun'] = self.currentRun
        if interval!=None:
            kwds['interval'] = interval
        if end!=None:
            kwds['end_time'] = end
        self._piccolo.piccolo.record(**kwds)

    def recordDark(self):
        self._piccolo.piccolo.dark()

    def autoIntegrate(self):
        self._piccolo.piccolo.setIntegrationTimeAuto()

    def setAutoIntegrationRepeats(self,auto):
        if auto <0:
            self.auto = -1
            self.autoIntegrateRepeat.setValue(-1)
            self.checkAutoIntegrate.setCheckState(0)
        else:
            self.auto = auto
            self.autoIntegrateRepeat.setValue(auto)
            self.checkAutoIntegrate.setCheckState(2)
        
    def changeAutoIntegrationRepeats(self):
        # get the GUI state
        enabled = (self.checkAutoIntegrate.checkState() == 2)
        if enabled:
            value = self.autoIntegrateRepeat.value()
        else:
            value = -1

        # check if new value is different from piccolo value
        if self.auto != value:
            self.auto = value
            self._piccolo.piccolo.setAuto(auto=value)

    def setCurrentRun(self,cr):
        self.currentRun = cr
        self.outputDir.setText(self.currentRun)
                
    def changeCurrentRun(self,cr=None):
        if cr is None:
            cr = str(self.outputDir.text())

        # check if new value is different from piccolo value
        if self.currentRun != cr:
            self.currentRun = cr
            self._piccolo.piccolo.setCurrentRun(cr=cr)

    def setNCycles(self,ncycles):
        self.nCycles = ncycles
        self.repeatMeasurements.setValue(self.nCycles)
            
    def changeNCycles(self):
        # get the GUI state
        value = self.repeatMeasurements.value()

        # check if new value is different from piccolo value
        if self.nCycles != value:
            self.nCycles = value
            self._piccolo.piccolo.setNCycles(ncycles=value)

    def setDelay(self,delay):
        self.delay = delay
        self.delayMeasurements.setValue(self.delay)
            
    def changeDelay(self):
        # get the GUI state
        value = self.delayMeasurements.value()

        # check if the new value is different from piccolo value
        if abs(self.delay - value)>1e-6:
            self.delay = value
            self._piccolo.piccolo.setDelay(delay=value)
                
    def pauseRecording(self):
        self._piccolo.piccolo.pause()

    def setRun(self):
        runList = self._piccolo.piccolo.getRunList()
        r = RunListDialog.getRun(runList=runList)
        if r is not None:
            self.changeCurrentRun(cr=r)
        
    def stopRecording(self):
        self._piccolo.piccolo.abort()'''

    def downloadSpectra(self, spectraName, direction=None):
        '''Downloads measurements of spectra for a certain direction
        
        :param spectraName: the name of a spectra
        :param direction: optional, e.g. Upwelling
        
        '''
        result = {}
        if self._piccolo!=None:
            spectra = self._piccolo.piccolo.getSpectra(fname=spectraName)
            if direction is None:
                direction = spectra.directions[0]
            brightness=[]
            for b in ['Light','Dark']:
                if spectra.haveSpectrum(b):
                    brightness.append(b)
            selectedSpectrum = brightness[0]
            piccoloSpectra = spectra.getSpectra(direction, selectedSpectrum)
            result['data'] = []
            for s in piccoloSpectra:
                xyList = self.generateXYlist(s.waveLengths, s.pixels)
                sDict = s.as_dict(pixelType='list')
                sDict['plotList'] = xyList
                sDict['Directions'] = spectra.directions
                result['data'].append(sDict)            
        return result


    def generateXYlist(self, x, y):
        '''Generate an XY list from two lists for plotting
        
        :param x: the list of x values
        :param y: the list of y values
        
        Structure of the returned data:
            [{
                x: 10,
                y: 20
            }, {
                x: 15,
                y: 10
            }]
        
        '''
        xyList=[]
        for i, val in enumerate(x):
            xyList.append({'x': x[i], 'y': y[i]})
        return xyList
    
    
    def getSpectraList(self, run=None):
        '''Returns a list with spectra names of a run
        
        :param run: default will be currentRun
        :returns: a list with spectraNames
        
        '''
        if run is None:
            run = self._piccolo.piccolo.getCurrentRun()
        fileList = self._piccolo.piccolo.getSpectraList(outDir=run)
        self._spectraList = fileList;
        return self._spectraList
        
    def getRunList(self):
        '''Returns all runs
        
        :returns: a list with runs
        
        '''
        self._runList = self._piccolo.piccolo.getRunList()
        return self._runList
    
    '''def setSpectrumAndDirection(self):
        self._selectedSpectrum = self.selectSpectrum.currentText()
        self._selectedDirection = self.selectShutter.currentText()
        if self._selectedSpectrum in ['Dark','Light'] and self._selectedDirection is not None:
            self.showSpectra()'''

    '''def showSpectra(self):
        self.spectraPlot.setTitle("{dir} {spec}".format(dir=self._selectedDirection,spec=self._selectedSpectrum))
        spectra = self._spectra.getSpectra(self._selectedDirection, self._selectedSpectrum)
        self.spectraPlot.plotSpectra(spectra)'''


    
    '''def updateMounted(self):
        info = self._piccolo.piccolo.info()
        self._piccoloInfo['datadir']=info['datadir']
        if info['datadir'] == 'not mounted':
            #self.mountDataButton.setText("mount data")
            pass
        else:
            #self.mountDataButton.setText("unmount data")
            pass'''
        
    '''def connectDialog(self):
        dialog = ConnectDialog()
        dialog.setConnection(self._connectionType,self._connectionData)
        data = dialog.getData()
        if data !=None:
            self.connect(data[0],data[1])'''

    '''def addSchedule(self):
        start,interval,end = ScheduleDialog.getSchedule()
        if start!=None:
            self.startRecording(start=start,end=end,interval=interval)'''

    '''def quietTimeDialog(self):
        # get current settings
        se = self._piccolo.getQuietTime()
        se = QuietTimeDialog.getQuietTime(start_time=se[0],end_time=se[1])
        if se is not None:
            self._piccolo.setQuietTime(start_time=se[0],end_time=se[1])'''
   


    
    
    def status(self):
        
        # save status here
        statusInfo = {}
        
        # check if we need to update times
        #now = datetime.datetime.now(tz=pytz.utc)
        #self.localTime.setText(now.strftime("%Y-%m-%dT%H:%M:%S"))
        
        if self._piccolo!=None:
            try:
                pass
                #ptime = self._piccolo.piccolo.getClock()
                #self.piccoloTime.setText(ptime.split('.')[0])
            except:
                pass
            try:
                pmem = self._piccolo.piccolo.memory()
                statusInfo['memory'] = pmem
                #self.percentMem.setValue(pmem)
            except:
                pass
            try:
                pcpu = self._piccolo.piccolo.cpu()
                statusInfo['cpu'] = pcpu
                #self.percentCPU.setValue(pcpu)
            except:
                pass
        
        
        # handle status
        state = 'red'
        status = 'disconnected'
        if self._piccolo != None:
            try:
                pstatus,estatus = self._piccolo.piccolo.status(listener=self._piccolo.listenerID)
            except:
                pstatus = piccolo2.PiccoloStatus.PiccoloStatus()
                pstatus.connected = False
                estatus = None
            
            if pstatus.connected:
                status = 'connected'
                state = 'green'
            else:
                status = 'disconnected'
                state = 'red'
            if pstatus.busy:
                status = 'busy'
                state = 'orange'
            if pstatus.paused:
                status += ', paused'
                #self.pauseRecordingButton.setText("Unpause")
            else:
                pass
                #self.pauseRecordingButton.setText("Pause")
            if pstatus.file_incremented:
                state = 'yellow'
                status += ', file_incr'
            msg=''
            if pstatus.new_message:
                msg = self._piccolo.piccolo.getMessage(listener=self._piccolo.listenerID)
                msg =msg.split('|')
                if msg[0] == 'IT':
                    spectrometer,shutter = msg[1:]
                    #self._times.updateIntegrationTimeDisplay(spectrometer,shutter)
                    value = self._times.getIntegrationTime(spectrometer,shutter)
                    row=self._times.spectrometers.index(spectrometer)
                    col =self._times.shutters.index(shutter)
                    self._piccoloInfo['integrationTimes'] = self._times.getIntegrationTimes()
                    self._piccoloInfo['message']={'type': 'integration', 'value': value, 'column': col, 'row': row}
                elif msg[0] == 'ITmin':
                    spectrometer = msg[1]
                    #self._times.updateIntegrationTimeDisplay(spectrometer,'min')
                    value = self._times.getIntegrationTime(spectrometer,'min')
                    row=self._times.spectrometers.index(spectrometer)
                    col =self._times.shutters.index('min')
                    self._piccoloInfo['integrationTimes'] = self._times.getIntegrationTimes()
                    self._piccoloInfo['message']={'type': 'integration', 'value': value, 'column': col, 'row': row}
                elif msg[0] == 'ITmax':
                    spectrometer = msg[1]
                    #self._times.updateIntegrationTimeDisplay(spectrometer,'max')
                    value = self._times.getIntegrationTime(spectrometer,'max')
                    row=self._times.spectrometers.index(spectrometer)
                    col =self._times.shutters.index('max')
                    self._piccoloInfo['integrationTimes'] = self._times.getIntegrationTimes()
                    self._piccoloInfo['message']={'type': 'integration', 'value': value, 'column': col, 'row': row}
                elif msg[0] == 'CR':
                    pass
                    #self.setCurrentRun(str(msg[1])) 
                elif msg[0] == 'AI':
                    pass
                    #self.setAutoIntegrationRepeats(int(msg[1]))
                elif msg[0] == 'NC':
                    pass
                    #self.setNCycles(int(msg[1]))
                elif msg[0] == 'D':
                    pass
                    #self.setDelay(float(msg[1]))
                elif msg[0] == 'warning':
                    pass
                    #QtGui.QMessageBox.warning(self,'Warning',msg[1],QtGui.QMessageBox.Ok)
            if estatus is not None and self._extendedStatus is not None:
                self._extendedStatus.update(estatus)
                if self._extendedStatus.isAutointegrating():
                    status += ' autointegrating'
                if self._extendedStatus.isRecording():
                    status += ' recording'
                    for s in self._extendedStatus.shutters:
                        status += ' %s '%s
                        if self._extendedStatus.isOpen(s):
                            status += '0'
                        else:
                            status += ' '

        if state=="green":
            pass
            #self.enableEdit()
        else:
            pass
            #self.disableEdit()
                            
        #self.statusLabel.setText(status)
        #self.statusLabel.setStyleSheet(' QLabel {color: %s}'%state)
        #self.repaint()
        statusInfo['state']=state
        statusInfo['status']=status
        statusInfo['msg']=msg
        return statusInfo
    
    
    
    
    def connect(self,connection,data):
        ok = True
        if connection == 'http':
            self._connectionType = 'http'
            self._connectionData = data
            self._piccolo = piccolo2.client.PiccoloJSONRPCClient(data)
        elif connection == 'xbee':
            self._connectionType = 'xbee'
            self._connectionData = data
            self._piccolo = piccolo2.client.PiccoloXbeeClient(data)
        else:
            ok = False
            errorTitle ='not implemented'
            errorMsg = 'connection type {} is not implemented yet'.format(connection)

        if ok:
            try:
                self._piccolo.connect()
            except:
                ok = False
                errorTitle = 'failed to connect'
                errorMsg = 'failed to connect to {}'.format(data)
            
        if not ok:
            raise Exception(errorTitle, errorMsg)
            return
        
        self._piccoloInfo['statusInfo'] = self.status()
        # get the server version
        self._piccoloInfo['piccoloVersion'] = self._piccolo.getVersion()
        # get the data dir
        info = self._piccolo.piccolo.info()
        self._piccoloInfo['datadir']=info['datadir']
        # initialise the extended status
        self._extendedStatus = PiccoloExtendedStatus(self._piccolo.piccolo.getSpectrometerList(),self._piccolo.piccolo.getShutterList())
        
        self.setPiccoloInfos()
        
        # hook up integration times
        self._times.piccoloConnect(self._piccolo.piccolo)
        self._piccoloInfo['integrationTimes'] = self._times.getIntegrationTimes()
        
        #download spectra List
        self.getSpectraList()
        

        
    def setPiccoloInfos(self):
        '''sets dynamic piccolo infos'''
        # get the current piccolo time
        ptime = self._piccolo.piccolo.getClock()
        #self.piccoloTime.setText(ptime.split('.')[0])
        self._piccoloInfo['piccoloTime']= ptime.split('.')[0]

        # hook up scheduler
        #self._scheduledJobs.piccoloConnect(self._piccolo)

        # set record parameters
        self._piccoloInfo['auto'] = self._piccolo.piccolo.getAuto()
        self._piccoloInfo['nCycles'] = self._piccolo.piccolo.getNCycles()
        self._piccoloInfo['delay'] = self._piccolo.piccolo.getDelay()
        self._piccoloInfo['currentRun'] = self._piccolo.piccolo.getCurrentRun()

        
    def updateIntegration(self, integration):
        for i in integration:
            self._times.updateIntegrationTime(**i)
     
        

    @property
    def piccoloInfo(self):
        return self._piccoloInfo
    
    @property
    def spectraList(self):
        return self._spectraList


    @property
    def runList(self):
        return self._runList

    
    def updateLoop(self, interval=2.0):
        '''Contacts the client to update the piccolo info every time interval
        
        :param interval: the interval to update, defaul is 2.0
        
        '''
        threading.Timer(interval, self.updateLoop).start()
        self._piccoloInfo['statusInfo'].update(self.status())
        self._piccoloInfo['integrationTimes'] = self._times.getIntegrationTimes()
        self.setPiccoloInfos()
        #get run list
        self.getRunList()
        #download spectra List
        self.getSpectraList()
    
    
    
    
def main(connection):
    pPiccolo = WebApp()
    pPiccolo.connect(connection[0],connection[1])
    pPiccolo.updateLoop()
    return pPiccolo

