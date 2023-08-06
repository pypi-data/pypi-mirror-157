import os,glob,re,pandas as pd,sys,pickle
from dorianUtils.utilsD import Utils
from dorianUtils.comUtils import Meteo_Client
import time
UNITS_DICT = {
    'kW':'JTW',
    'kWh':'JTWH',
    'kVA':'JTVA',
    'kvar':'JTVar',
    'kvarh':'JTVarH',
    'kVAh':'JTVAH',
    }
###############
#  FUNCTIONS  #
###############

def __makemodebus_mapUnique(modebus_map):
    '''make modebus_map unique'''
    uniquemodebus_map = []
    for tag in modebus_map['id'].unique():
        dup=modebus_map[modebus_map['id']==tag]
        ### privilege on IEEE754 strcuture if duplicates
        rowFloat = dup[dup['type']=='IEEE754']
        if len(rowFloat)==1:
            uniquemodebus_map.append(rowFloat)
        else :
            uniquemodebus_map.append(dup.iloc[[0]])
    uniquemodebus_map=pd.concat(uniquemodebus_map).set_index('id')
    return uniquemodebus_map

def __build_plc_from_modebus_map(modebus_map,build_description=True,build_unite=True):
    dfplc = pd.DataFrame()
    if build_description:
        dfplc['DESCRIPTION'] = modebus_map.apply(lambda x:VARIABLES.loc[x['description'],'description']+ ' ' + COMPTEURS.loc[x['point de comptage'],'description'],axis=1)
    else:
        dfplc['DESCRIPTION'] = modebus_map['description']

    if build_unite:
        dfplc['UNITE'] = modebus_map['unit'].apply(lambda x:UNITS_DICT[x])
    else:
        dfplc['UNITE'] = modebus_map['unit']
    # dfplc.index    = modebus_map.index
    dfplc['MIN']      = -200000
    dfplc['MAX']      = 200000
    dfplc['DATATYPE'] = 'REAL'
    dfplc['DATASCIENTISM'] = True
    dfplc['PRECISION'] = 0.01
    dfplc['VAL_DEF'] = 0
    return dfplc

def __getSizeOf(typeVar,f=1):
    if typeVar == 'IEEE754':return 2*f
    elif typeVar == 'INT64': return 4*f
    elif typeVar == 'INT32': return 2*f
    elif typeVar == 'INT16': return 1*f
    elif typeVar == 'INT8': return f/2

def __parseXML_VMUC(xmlpath):
    import xml.etree.ElementTree as ET

    def findInstrument(meter):
        df=[]
        for var in meter.iter('var'):
            df.append([var.find('varaddr').text,
                int(var.find('varaddr').text[:-1],16),
                var.find('vartype').text,
                __getSizeOf(var.find('vartype').text,1),
                __getSizeOf(var.find('vartype').text,2),
                var.find('vardesc').text,
                var.find('scale').text,
                var.find('unit').text]
                )
        df = pd.DataFrame(df)
        df.columns=['adresse','intAddress','type','size(mots)','size(bytes)','description','scale','unit']
        df['slave_unit'] = meter.find('addrTCP').text
        df['point de comptage']=meter.find('desc').text
        return df

    tree = ET.parse(xmlpath)
    root = tree.getroot()
    dfs=[]
    for meter in root.iter('meter'):
        dfs.append(findInstrument(meter))
    df=pd.concat(dfs)
    df['id']=[re.sub('[\( \)]','_',k) + '_' + l for k,l in zip(df['description'],df['point de comptage'])]
    df['slave_unit'] = pd.to_numeric(df['slave_unit'],errors='coerce')
    df['scale'] = pd.to_numeric(df['scale'],errors='coerce')
    return df

def __vmuc_mbmap():
    vmuc_modebus_map = __parseXML_VMUC(VMUC_FILE_XML)
    vmuc_modebus_map = __makemodebus_mapUnique(vmuc_modebus_map)
    ############ keep only variables of interest
    var_vmuc = ['kW sys','kWh','kW L1', 'kW L2', 'kW L3','kVA L1', 'kVA L2', 'kVA L3','kWh L1', 'kWh L2', 'kWh L3']
    vmuc_modebus_map = vmuc_modebus_map[vmuc_modebus_map.description.isin(var_vmuc)]
    ############# appliquer la convention de nommage pour la definition des tags
    vmuc_modebus_map.index=vmuc_modebus_map.apply(lambda x:COMPTEURS.loc[x['point de comptage'],'fullname']+'-'+x['description']+'-'+UNITS_DICT[x['unit']],axis=1)
    return vmuc_modebus_map

def __smartlogger_mbmap():
    sl_modebusmap = pd.DataFrame()
    sl_modebusmap['adresse']     = [40525,40560]
    sl_modebusmap['intAddress']  = sl_modebusmap['adresse']
    sl_modebusmap['type']        = 'INT32'
    sl_modebusmap['size(mots)']  = 2
    sl_modebusmap['size(bytes)'] = 4
    sl_modebusmap['description'] = ['kW','kWh']
    sl_modebusmap['scale']       = [1/1000,1/10]
    sl_modebusmap['unit']        = ['kW','kWh']
    sl_modebusmap['slave_unit']  = 1
    sl_modebusmap['point de comptage'] = 'centrale SLS 80kWc'
    sl_modebusmap.index = sl_modebusmap['point de comptage']+'-'+sl_modebusmap['description']
    ############# appliquer la convention de nommage pour la definition des tags
    sl_modebusmap.index=sl_modebusmap.apply(lambda x:COMPTEURS.loc[x['point de comptage'],'fullname']+'-'+x['description']+'-'+UNITS_DICT[x['unit']],axis=1)
    return sl_modebusmap

def __site_sls_mbmap():
    sitesls_mbmap = pd.DataFrame()
    sitesls_mbmap['adresse']     = [4198,4200,4246,4300]
    sitesls_mbmap['intAddress']  = sitesls_mbmap['adresse']
    sitesls_mbmap['type']        = 'UINT32'
    sitesls_mbmap['size(mots)']  = 2
    sitesls_mbmap['size(bytes)'] = 4
    sitesls_mbmap['unit']       = ['kW','kW','kWh','kWh']
    sitesls_mbmap['scale']       = 1
    sitesls_mbmap['slave_unit']  = 20
    sitesls_mbmap['description'] = ['puissance_soutirage','puissance_injection','energie_soutirage','energie_injection']
    sitesls_mbmap['point de comptage'] = 'siteSLS'
    sitesls_mbmap.index = sitesls_mbmap['point de comptage']+'-'+sitesls_mbmap['description']
    ############# appliquer la convention de nommage pour la definition des tags
    sitesls_mbmap.index=sitesls_mbmap.apply(lambda x:COMPTEURS.loc[x['point de comptage'],'fullname']+'-'+x['description']+'-'+UNITS_DICT[x['unit']],axis=1)
    return sitesls_mbmap

def __parse_object_name(x):
    reg_exp=r"(?P<description>[\w\s°]+) (?P<address>[0-9A-F]{4}h) (?P<unitname>\w+) (?P<unit>Wh?) / PASSERELLE MODBUS (?P<passerelle>[\w\s]+)"
    m=re.match(reg_exp, x)
    if m is None:
        # return [x,'','','']
        return [x,'']
    else:
        # return [m.group('description'),m.group('address'),m.group('unitname'),m.group('unit'),m.group('passerelle')]
        return [m.group('description'),m.group('unit')]

def __gtc_modebus_map(df_gtc,debug=False):
    len_parsed_df = df_gtc['object-name'].apply(lambda x:len(__parse_object_name(x)))
    parsed_df     = df_gtc['object-name'].apply(lambda x:__parse_object_name(x))
    idxbugs=len_parsed_df[len_parsed_df==0].index
    parsed_df = parsed_df.drop(idxbugs)
    modebusmap=pd.DataFrame(parsed_df.tolist(), index= parsed_df.index,columns=['description','unit'])
    modebusmap['adresse']     = df_gtc.loc[modebusmap.index,'Adresse MODBUS']
    modebusmap['intAddress']  = modebusmap['adresse']
    modebusmap['type']        = 'IEEE754'
    modebusmap['size(mots)']  = 2
    modebusmap['size(bytes)'] = modebusmap['size(mots)']*2
    modebusmap['scale']       = 1/1000
    modebusmap['slave_unit']  = 1
    modebusmap['unit']  = 'k'+modebusmap['unit']
    if debug:
        print(idxbugs)
        int(df_gtc.loc[idxbugs[0],'object-name'])
        return idxbugs
    return modebusmap

def __gtc_alstom_plc():
    df_gtc = pd.read_excel(FILECONF_MONITORING,sheet_name='ALSTOM_MODBUS_MBA_SYLFEN')
    gtc_modebus_map = __gtc_modebus_map(df_gtc)
    ############ keep only variables of interest
    gtc_modebus_map = gtc_modebus_map[gtc_modebus_map['description'].str.contains('(TD)|(TGBT)')]

    ############# appliquer la convention de nommage pour la definition des tags
    df_compteurs_desc = COMPTEURS[COMPTEURS.device=='gtc_alstom'].reset_index().set_index('description')
    desc2fullname   = df_compteurs_desc['fullname'].to_dict()
    desc2ptComptage = df_compteurs_desc['pointComptage'].to_dict()
    gtc_modebus_map.index                = gtc_modebus_map.apply(lambda x:desc2fullname[x['description']] + '-' + UNITS_DICT[x['unit']],axis=1)
    gtc_modebus_map['point de comptage'] = gtc_modebus_map.apply(lambda x:desc2ptComptage[x['description']],axis=1)
    gtc_modebus_map['description']       = gtc_modebus_map['unit']
    ############## build plc file from modebusmap
    gtc_plc = __build_plc_from_modebus_map(gtc_modebus_map)
    return gtc_modebus_map,gtc_plc

def quick_modbus_reading():
    # from monitoringBuilding import conf
    from pymodbus.client.sync import ModbusTcpClient
    from pymodbus.payload import BinaryPayloadDecoder
    from pymodbus.constants import Endian

    client = ModbusTcpClient(conf.DF_DEVICES.loc['gtc_alstom'].IP, port=502)
    client.connect()

    result = client.read_holding_registers(0, 2, unit=1)
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Little, wordorder=Endian.Little)
    value = decoder.decode_32bit_float()
    print(value)

def quick_modbus_okwind_reading():
    from pymodbus.client.sync import ModbusTcpClient
    from pymodbus.payload import BinaryPayloadDecoder
    from pymodbus.constants import Endian
    UNIT=0x08
    client = ModbusTcpClient(DF_DEVICES.loc['tracker_okwind'].IP, port=502)
    client.connect()

    result = client.read_holding_registers(1000, 2, unit=UNIT)
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)
    plant_production = decoder.decode_32bit_uint() / 10 # divide by the gain
    plant_production = decoder.decode_32bit_uint() / 10 # divide by the gain

    result = client.read_holding_registers(1021, 1, unit=UNIT)
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)
    inverter_number = decoder.decode_16bit_uint() # gain is 1

    print('Plant production: %skW' % plant_production)
    print('Inverter number: %s' % inverter_number)

    client.close()

def __tracker_okwind_mbmap():
    dtypes={'U32':'UINT32','U16':'UINT16', 'I32':'INT32', 'I16':'INT16', 'F32':'IEEE754'}
    tracker_okwind_mbmap=pd.read_excel(FILECONF_MONITORING,sheet_name='ok_wind_tracker_modbus')
    tracker_okwind_mbmap['type']=tracker_okwind_mbmap['type'].apply(lambda x:dtypes[x])
    tracker_okwind_mbmap['scale']=1/tracker_okwind_mbmap['scale']
    # tracker_okwind_mbmap.columns=[c.upper() for c in tracker_okwind_mbmap.columns]
    # tracker_okwind_mbmap.index=
    tracker_okwind_mbmap['slave_unit']=0x08
    tracker_okwind_mbmap.index=tracker_okwind_mbmap.apply(lambda x:COMPTEURS.loc['tracker_okwind','fullname']+'-'+x['tag']+'-'+x['unit'],axis=1)
    tracker_okwind_mbmap['point de comptage']='tracker_okwind'
    return tracker_okwind_mbmap

def generate_conf_monitoring():
    print('generating configuration files and store in :'+FILECONF_MONITORING_PKL)
    start=time.time()
    plcs,modebus_maps={},{}
    modebus_maps['vmuc'] = __vmuc_mbmap()
    plcs['vmuc']         = __build_plc_from_modebus_map(modebus_maps['vmuc'])

    modebus_maps['smartlogger'] = __smartlogger_mbmap()
    plcs['smartlogger']         = __build_plc_from_modebus_map(modebus_maps['smartlogger'])

    modebus_maps['site_sls'] = __site_sls_mbmap()
    plcs['site_sls']         = __build_plc_from_modebus_map(modebus_maps['site_sls'])

    modebus_maps['tracker_okwind'] =__tracker_okwind_mbmap()
    plcs['tracker_okwind']         =__build_plc_from_modebus_map(modebus_maps['tracker_okwind'],False,False)

    modebus_maps['gtc'],plcs['gtc'] = __gtc_alstom_plc()
    plcs['meteo']                   = Meteo_Client().dfplc
    useful_tags=pd.read_excel(FILECONF_MONITORING,sheet_name='useful_tags',index_col=0)


    f = open(FILECONF_MONITORING_PKL,'wb')
    pickle.dump(plcs,f)
    pickle.dump(modebus_maps,f)
    pickle.dump(useful_tags,f)

    f.close()
    print('configuration files all generated in  : '+ str(time.time()-start)+' seconds.')
    return [plcs,modebus_maps,useful_tags]

###########################################
##### GLOBAL VARIABLES CONFIGURATION ######
###########################################
#### default parameters
PARKING_TIME  = 1*3600
DB_PARAMETERS = {
    'host'     : "localhost",
    'port'     : "5432",
    'dbname'   : "bigbrother",
    'user'     : "postgres",
    'password' : "sylfenbdd"
    }
DB_TABLE='realtimedata'
TZ_RECORD='UTC'
ACTIVE_DEVICES = [
    'vmuc',
    'smartlogger',
    'site_sls',
    'meteo'
    # 'tracker_okwind',
    # 'gtc_alstom',
]
#############################################
# user parameters are in parameters_conf.py
# and will overwrite default parameters
#############################################
if os.path.exists(os.path.dirname(__file__) + '/parameters_conf.py'):
    from .parameters_conf import *

__appdir = os.path.dirname(os.path.realpath(__file__))
PARENTDIR = os.path.dirname(__appdir)
CONFFOLDER = __appdir+'/confFiles/'
LOG_FOLDER = PARENTDIR+'/logs/'
FILECONF_MONITORING=CONFFOLDER + 'monitorbuilding_configfiles.ods'
FILECONF_MONITORING_PKL=CONFFOLDER + 'monitoring_conf.pkl'
VMUC_FILE_XML = CONFFOLDER + 'ModbusTCP_Map_2022_05_28.xml'


if 'sylfen' in os.getenv('HOME'):
    baseFolder   = '/home/sylfen/data_ext/'
else:
    baseFolder = '/home/dorian/data/sylfenData/'

FOLDERPKL  = baseFolder + 'monitoring_daily/'
DF_DEVICES = pd.read_excel(FILECONF_MONITORING,index_col=0,sheet_name='devices')
VARIABLES  = pd.read_excel(FILECONF_MONITORING,index_col=0,sheet_name='variables')

def __build_fullnames_counts():
    compteurs  = pd.read_excel(FILECONF_MONITORING,index_col=0,sheet_name='compteurs')
    dictCat  = DF_DEVICES.category.to_dict()
    compteurs['fullname']=list(compteurs.reset_index().apply(lambda x:dictCat[x['device']] + '-' + x['pointComptage']+'-',axis=1))
    for cat in ['C','PV']:
        devices = list(DF_DEVICES[DF_DEVICES.category==cat].index)
        locCompteurs = compteurs[compteurs.device.isin(devices)].reset_index()
        if not locCompteurs.empty:
            compteursNumber = locCompteurs.reset_index().index.to_series().apply(lambda x:'{:x}'.format(x+1).zfill(8))
            fullnames       = cat + compteursNumber + '-' + locCompteurs['pointComptage']
            compteurs.loc[locCompteurs['pointComptage'],'fullname'] = list(fullnames)
    return compteurs
COMPTEURS = __build_fullnames_counts()
#
if os.path.exists(FILECONF_MONITORING_PKL):
    monitoring_objs= Utils().loads_pickle(FILECONF_MONITORING_PKL)
else:
    monitoring_objs=generate_conf_monitoring()

[PLCS,MODEBUS_MAPS,USEFUL_TAGS] = monitoring_objs

DF_PLC = pd.concat(PLCS.values(),axis=0)

# del os,glob,re,pd,sys,pickle,time,baseFolder,Meteo_Client,monitoring_objs
