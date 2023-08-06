#!/bin/python
import importlib,time,sys,os
start=time.time()
import pandas as pd
# import dorianUtils.comUtils as comUtils
from dorianUtils.comUtils import print_file
# from monitorBuilding.monitorBuilding import MonitorBuilding_dumper
from monitorBuilding import (conf,monitorBuilding)
importlib.reload(monitorBuilding)
print('monitorBuilding loaded in ',time.time()-start,' seconds')

# log_file = None
# log_file = conf.LOG_FOLDER + '/dumper_monitorBuilding.log'
__appdir = os.path.dirname(os.path.realpath(__file__))
PARENTDIR = os.path.dirname(__appdir)

log_file = PARENTDIR+ '/logs/dumper_monitorBuilding.log'
print_file(' '*30 + 'START MONITORING DUMPER' + '\n',filename=log_file,mode='w')
# dumper_screenBuilding = MonitorBuilding_dumper()
dumper_monitoring = monitorBuilding.MonitorBuilding_dumper(log_file_name=log_file)
# dumper_monitoring.park_database()
dumper_monitoring.start_dumping()

# vmuc  = dumper_monitoring.devices['vmuc']
# meteo = dumper_monitoring.devices['meteo']
# meteo.start_auto_reconnect()
# df=meteo.collectData()
# print(df)
