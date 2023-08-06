#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Python library to retrieve climate statistics from DWD CDC.

Date provided by Climate Data Center (CDC) of Deutscher WetterDienst (DWD)
are retrieved from opendata.dwd.de and simple statistics on
hourly, daily and monthly basis are calulated.

Statistics are returned matching a provided list of dates.

The statistics are cached in the user home directory for subsequent calls.
The DWD server is regularly checked for updates and statistics are updated,
if necessary. Updates can be triggerd manually, too.
'''

import os
import ftplib
from io import StringIO
import tempfile
import sys
import zipfile

import numpy as np
import pandas as pd

from .__version__ import __title__, __description__, __version__
from .__version__ import __url__, __author__, __author_email__
from .__version__ import __license__, __copyright__

import logging

try:
    import metlib as m
    metlib = True
except ImportError:
    metlib = False

this = sys.modules[__name__]

_MODULENAME = 'cdcclimate'
_CACHEDIR = os.path.join(os.path.expanduser('~/.cache'),_MODULENAME)
_CLIMATEDB = 'cdcclimate_{:05d}.db'

_TMPDIR = tempfile.TemporaryDirectory()
_SERVER_ADDRESS = "opendata.dwd.de"
_SERVER_PATH = "/climate_environment/CDC/observations_germany/climate/"

_OUTPUTS = {
    'hourly':  {'t': 'TT_TU',
                'p': 'P0',
                'w': 'F',
                'r': 'R1',
                's': 'GLOBAL_KW',
                'u': 'V_TE010',
                },
    'daily':   {'t': 'TMK',
                'p': 'PM',
                'w': 'FM',
                'r': 'RSK',
                's': 'GLOBAL_KW',
                'h': 'SD_STRAHL',
                'u': 'V_TE010M',
                },
    'monthly': {'t': 'MO_TT',
                'r': 'MO_RR',
                'h': 'MO_SD_S',
                'w': 'MO_FK',
                }
    }
_KINDS = list(_OUTPUTS.keys())

_CHECK_INTERVAL = pd.Timedelta(4,'W')  # four weeks

_OLDEST = pd.to_datetime(0)
_LENYEAR = 30
_LASTYEAR = None
_FASTRED = True

def _ftp_list(station:int, kind):
    if kind=='hourly':
        param_names={
            "TU": "air_temperature",
            "P0": "pressure",
            "FF": "wind",
            "RR": "precipitation",
            "ST": "solar",
            "EB": "soil_temperature",
            "CS": "cloud_type",
        }
        prefix='stundenwerte'
    elif kind=='daily':
        param_names={
            "KL": "kl",
            "EB": "soil_temperature",
            "ST": "solar",
        }
        prefix='tageswerte'
    elif kind=='monthly':
        param_names={
            "KL": "kl",
        }
        prefix='monatswerte'
    else:
        raise ValueError('unknown kind: %s'%kind)
    ftpfiles = {}
    ftp = ftplib.FTP(_SERVER_ADDRESS)
    ftp.login()                       # anonymous
    ftp.makepasv()
    ftp.cwd(os.path.join(_SERVER_PATH,kind))
    for x,p in param_names.items():
        if p == 'solar':
            pattern = "{:s}/{:s}_{:s}_%05d_row.zip".format(p,prefix,x)
        else:
            pattern = "{:s}/historical/{:s}_{:s}_%05d_*_hist.zip".format(p,prefix,x)
        logging.debug('searching: "%s"'%pattern)
        flist = ftp.nlst(pattern % station)
        for f_name in flist:
            # MLST not supported by opendata.dwd.de
            #for k,v in ftp.mlsd(f_name):
            #    if k == 'modify':
            #        f_date = pd.to_datetime(v)
            #    if k == 'size':
            #        f_size = int(v)

            # SIZE and MDTM are supported
            f_size = ftp.size(f_name)
            # MDTM not supported by ftplib: https://stackoverflow.com/a/29027386
            timestamp = ftp.voidcmd("MDTM {:s}".format(f_name))[4:].strip()
            f_date = pd.to_datetime(timestamp)

            ftpfiles[f_name] ={'size': f_size, 'date': f_date, 'group': x}
    ftp.close()
#    for k,v in ftpfiles.items():
#        logging.debug('found: %s: %s'%(k,format(v)))
    return ftpfiles

def _ftp_download(ftpfiles,kind):
    ftp = ftplib.FTP(_SERVER_ADDRESS)
    ftp.login()                       # anonymous
    ftp.makepasv()
    ftp.cwd(os.path.join(_SERVER_PATH,kind))
    zipfiles = {}
    for f_name,f_facts in ftpfiles.items():
        z_name = os.path.basename(f_name)
        z_file = os.path.join(_TMPDIR.name, z_name)
        logging.info ('downloading new %s'%z_name)
        with open(z_file, 'wb') as fid:
            ftp.retrbinary('RETR '+f_name, fid.write)
        zipfiles[z_name] = f_facts['group']
    ftp.close()
    return zipfiles


def _remove_files(files:dict):
    for f in files:
        logging.debug('removing file: %s'%f)
        os.remove(os.path.join(_TMPDIR.name, f))
    return

def _extract_meta(zipfiles:dict):
    metafiles = ['Metadaten_Geographie_05100.txt']
    for z,var in zipfiles.items():
        logging.debug('processing zipfile: %s'%z)
        zo = zipfile.ZipFile(os.path.join(_TMPDIR.name,z))
        zl = zo.namelist()
        for f in metafiles:
            if f in zl:
                logging.debug('extracting metafile: %s'%f)
                zo.extract(f, _TMPDIR.name)
    return metafiles

def _extract_hist(zipfiles:dict, kind):
    if kind=='hourly':
        pattern = {v: 'produkt_%2s_stunde'%v.lower() for k,v in zipfiles.items()}
    elif kind=='daily':
        pattern = {'KL': 'produkt_klima_tag',
                   'EB': 'produkt_erdbo_tag',
                   'ST': "produkt_st_tag",
                   }
    elif kind=='monthly':
        pattern = {'KL': 'produkt_klima_monat',
                   }
    else:
        raise ValueError('unknown kind: %s'%kind)
    datafiles = {}
    for z,var in zipfiles.items():
        logging.debug('processing zipfile: %s'%z)
        zo = zipfile.ZipFile(os.path.join(_TMPDIR.name,z))
        zl = zo.namelist()
        for f in zl:
            if f.startswith(pattern[var]):
                logging.debug('extracting datafile: %s'%f)
                zo.extract(f, _TMPDIR.name)
                datafiles[f] = var
        del(zo)
    return datafiles

def _read_meta(station:int, metafiles:list):
    for stninfo in metafiles:
        logging.info("read station info from: %s"%stninfo)
        path = os.path.join(_TMPDIR.name, stninfo)
        df=pd.read_csv(path,sep=' *; *', engine='python',header=0)
        logging.debug('columns'+'|'.join(df.columns))
        for i,l in df.iterrows():
            if l['Stations_id'] == station:
                ele = l['Stationshoehe']
                lat = l['Geogr.Breite']
                lon = l['Geogr.Laenge']
                nam = l['Stationsname']
                # stop reading this file
                break
        else:
            # not found in this file
            continue
        # stop reading all files
        break
    else:
        # not in any file
        raise ValueError('station not found: %i'%station)
    # break leads here
    logging.debug("station name: %s"%nam)
    return({'lat': lat, 'lon': lon, 'ele': ele, 'nam': nam})

def _read_hist(datafiles:dict, kind:str):
    if kind=='hourly':
        param_cols={
            "TU": ['RF_TU',    # 2m air temperature  °C
                   'TT_TU',    # 2m relative humidity  %
                   ],
            "P0": ['P',        # mean sea level pressure  hPa
                   'P0',       # pressure at station height  hPa
                   ],
            "FF": ['D',        # mean wind direction  deg
                   'F',        # mean wind speed  m/s
                   ],
            "RR": ['R1'],
            "ST": ['ATMO_LBERG', # hourly sum of longwave downward radiation  J/cm²
                   'FG_LBERG', # hourly sum of solar incoming radiation  J/cm^2
                   'SD_LBERG', # hourly sum of sunshine duration  min
                   ],
            "EB": ['V_TE002',  # soil temperature in  2 cm depth  °C
                   'V_TE005',  # soil temperature in  5 cm depth  °C
                   'V_TE010',  # soil temperature in 10 cm depth  °C
                   'V_TE020',  # soil temperature in 20 cm depth  °C
                   'V_TE050',  # soil temperature in 50 cm depth  °C
                   'V_TE100',  # soil temperature in  1 m  depth  °C
                   ],
            "CS": ['V_N',      # total cloud cover  octa
                   'V_S1_HHS', # height of 1.layer  m
                   ],
        }
    elif kind=='daily':
        param_cols={
            "KL": ['TNK',  #  daily minimum of temperature at 2m height  °C
                   'TMK',  #  daily mean of temperature  °C
                   'TXK',  #  daily maximum of temperature at 2m height  °C
                   'VPM',  #  daily mean of vapor pressure  hPa
                   'PM',   #  daily mean of pressure (QFE?)  hPa
                   'FM',   #  daily mean of wind speed  m/s
                   'FX',   #  daily maximum of wind gust  m/s
                   'RSK',  #  daily precipitation height  mm
                   'NM',   #  daily mean of cloud cover  octa
                   ],
            "ST": ['ATMO_STRAHL', # daily sum of longwave downward radiation  J/cm^2
                   'FG_STRAHL',   # daily sum of solar incoming radiation J/cm^2
                   'SD_STRAHL',   # daily sum of sunshine duration  h
                   ],
            "EB": ['V_TE002M', # daily soil temperature in  2 cm depth  °C
                   'V_TE005M', # daily soil temperature in  5 cm depth  °C
                   'V_TE010M', # daily soil temperature in 10 cm depth  °C
                   'V_TE020M', # daily soil temperature in 20 cm depth  °C
                   'V_TE050M', # daily soil temperature in 50 cm depth  °C
                   ],
        }
    elif kind=='monthly':
        param_cols={
            "KL": [
                   'MO_FK', # monthly mean of wind speed in Bft  Bft
                   'MO_N',  # monthly mean of cloud cover  octa
                   'MO_RR', # monthly sum of precipitation height  mm
                   'MO_SD_S', # monthly sum of sunshine duration  Stunde
                   'MO_TN', # monthly mean of air temperature minimum  °C
                   'MO_TT', # monthly mean of air temperature at 2m height  °C
                   'MO_TX', # monthly mean of air temperature maximum  °C
                   'MX_RS', # Maximale precipitation height des Monats  mm
                   'MX_TN', # absolute minimum of air temperature at 2m height  °C
                   'MX_TX', # absolute maximum of air temperature at 2m height  °C
                   ],
        }
    else:
        raise ValueError('unknown kind: %s'%kind)
    dat = None
    for var in set(datafiles.values()):
        logging.debug('assembling variable %s'%var)
        dat_var = None
        for daf,v in datafiles.items():
            if v != var:
                continue
            logging.info ('reading %s' % daf)
            path = os.path.join(_TMPDIR.name, daf)
            dati=pd.read_csv(path, sep=' *; *', engine='python',header=0)
            logging.debug('columns'+'|'.join(dati.columns))
            if not 'MESS_DATUM' in dati.columns and 'MESS_DATUM_BEGINN' in dati.columns:
                dati['MESS_DATUM'] = [str(x)[0:6]+'01' for x in dati['MESS_DATUM_BEGINN']]
            if dati['MESS_DATUM'].dtype in [np.dtype(str),np.object] :
              dati['time']=pd.to_datetime(list(map(lambda s: (s.strip()+'0000')[0:10], dati['MESS_DATUM'])),format="%Y%m%d%H", utc=True)
            elif dati['MESS_DATUM'].dtype==np.int64 :
              dati['time']=pd.to_datetime(list(map(lambda s: ('{:d}0000'.format(s))[0:10], dati['MESS_DATUM'])),format="%Y%m%d%H",  utc=True)
            else:
              logging.critical('unknown column dtype {:s}'.format(str(dati['MESS_DATUM'].dtype)))
              quit(1)
            dati = dati.set_index('time')
            # select only wanted columns
            logging.debug ('"%s": "%s" -> "%s"'%(daf,v,param_cols[v]))
            #dati=dati.drop(['STATIONS_ID','MESS_DATUM','eor'],axis=1)
            dati = dati[param_cols[v]]
            logging.debug('time range %s -- %s'%(format(np.min(dati.index)),
                                                 format(np.max(dati.index))))

            if dat_var is None:
                dat_var = dati
            else:
                logging.info('appendig data of variable %s'%var)
                dat_var.merge(dati, how='outer')
        if dat_var is None:
            logging.error('no data of variable %s'%var)
            continue
        if dat is None:
            dat = dat_var
            logging.info('creating new table: variable %s'%var)
        else:
            dat=pd.merge(dat, dat_var, how='outer', left_index=True, right_index=True )
            logging.info('merging into table: variable %s'%var)

    logging.debug(dat.columns)
    return(dat)


def _data_contitioning(dat:pd.DataFrame, stationinfo:dict, kind:str,
                      lenyear:int=30, lastyear:int=None, fastred=True):
    if kind=='hourly':
        freq='H'
    elif kind=='daily':
        freq='D'
    elif kind=='monthly':
        freq='M'
    else:
        raise ValueError('unknown kind: %s'%kind)
    logging.info ('make time axis regular')
    N1 = dat.shape[0]
    idx = pd.date_range(dat.index.min(), dat.index.max(), freq=freq)
    dat = dat.reindex(idx, fill_value=np.nan)
    N2 = dat.shape[0]
    logging.debug ('added time values: %d'%(N2-N1))
    del(N1,N2)
    #
    logging.info('mark missing values as nan')
    #
    for col in dat.columns:
        logging.debug ("column {:s}".format(col))
        if pd.api.types.is_numeric_dtype(dat[col].dtype):
            dat.loc[ dat[col].apply(lambda x: int(x) if pd.notnull(x) else x) == -999 , col ] = np.nan
        elif pd.api.types.is_string_dtype(dat[col].dtype):
            dat[col] = [x.replace('-999','') if not pd.isna(x) else x for x in dat[col]]
            dat[col] = dat[col].where(dat[col] == '', np.nan)
        else:
            logging.debug('skipped')
    #
    #
    logging.info ("correct coding errors")
    #
    for col in dat.columns:
        if col in ['P']:
            logging.debug ("column {:s}".format(col))
            colav = dat[col].mean()
            colsd = dat[col].std()
            dat[col] = dat[col].where( abs(dat[col]-colav) > 3.5*colsd, np.nan)
    # no additional corrections needed for quality controlled CDC data
    #

    #
    logging.info ("fill missing values")
    #
    for col in dat.columns:
        logging.debug ("column {:s}".format(col))
        if pd.api.types.is_float_dtype(dat[col].dtype):
           dat[col] = dat[col].interpolate(method='time',
              limit_area='inside')
    #
    logging.info ("convert J/cm^2 to W/m^2")
    #
    if kind == 'hourly':
        #
        #
        if 'FD_LBERG' in dat.columns:
            dat['DIFFUS_KW']=dat['FD_LBERG']*10000./3600.
        if 'FG_LBERG' in dat.columns:
            dat['GLOBAL_KW']=dat['FG_LBERG']*10000./3600.
    elif kind == 'daily':
        #
        logging.info ("convert J/dcm^2 to W/m^2")
        #
        if 'FD_STRAHL' in dat.columns:
            dat['DIFFUS_KW']=dat['FD_STRAHL']*10000./(24.*3600.)
        if 'FG_STRAHL' in dat.columns:
            dat['GLOBAL_KW']=dat['FG_STRAHL']*10000./(24.*3600.)
        #
    elif kind == 'monthly':
        pass

    #
    logging.info ("calculate evapotranspiration")
    #
    if kind in ['hourly']:
        z0=1.
        dat['F2'] = [ m.wind.transfer(m.wind.LogWind(u=x,z=10,z0=z0),z0=z0).u(2.) for x in dat['F']]
        dat['ETa'] = m.penmanmonteith('TT_TU','RF_TU','F2','P0','GLOBAL_KW',df=dat,
                               lat=50,ele=250,hPa=True,percent=True)
        # dat['ETa'] = ETa.resample(rule,label='right',closed='right').mean()

    #
    logging.info ("reverse station reduction to sea-level pressure")
    #
    #
    if 'P' in dat.columns and 'P0' in dat.columns:
        #
        # DWD-Formel Druckreduktion
        #
        #p = ps *EXP(gn*h/(R*(t+m.Tzero+C*e+gam*h/2)))
        #
        #t momentane Stationstemperatur in °C
        #e momentaner Stationsdampfdruck in hPa (evtl. auch zu vernachlässigen)
        #ps momentaner Stationsluftdruck in hPa (=QFE)
        #h Stationshöhe in Metern (oder besser geopotentiellen Metern)
        #
        gam = 0.0065 #K/gpm
        C = 0.11 #K/hPa DWD-Beiwert für die Berücksichtigung der Feuchte, etwas stationsabhängig aber irrelevant
        h = stationinfo['ele']
        #
        if not fastred:
            for i in range(0,len(dat)):
                if ( ~np.isnan(dat['P'][i]) or np.isnan(dat['P0'][i]) ):
                    continue
                t=dat['TT_TU'][i]
                e=m.esat_w(dat['TT_TU'][i], Kelvin=False, hPa=True) * dat['RF_TU'][i] / 100.
                dat.iloc[i,dat.columns.get_loc('P')]=dat['P0'][i]/np.exp(m.gn*h/(m.R*(t+m.Tzero+C*e+gam*h/2)))
        else:
            t=np.nanmean(dat['TT_TU'])
            e=m.esat_w(t, Kelvin=False, hPa=True) * np.nanmean(dat['RF_TU']) / 100.
            redfact=np.exp(m.gn*h/(m.R*(t+m.Tzero+C*e+gam*h/2)))
            dat['P']=dat['P'].where(np.isnan(dat['P0']),dat['P0']/redfact)

    logging.info ("limit time interval")
    if lastyear is None:
        time_stop = dat.index[-1]
    else:
        time_stop = pd.Timestamp(year=lastyear, month=12, day=31,
                                 hour=23, minute=59, tz=dat.index[-1].tz)
    time_start = pd.Timestamp(year=time_stop.year - 30,
                              month=time_stop.month,
                              day=time_stop.day,
                              hour=time_stop.hour,
                              minute=time_stop.minute,
                              tz=time_stop.tz)
    dat = dat.loc[ (dat.index >= time_start) & (dat.index <= time_stop) ]
    logging.debug('time range %s -- %s'%(format(np.min(dat.index)),
                                         format(np.max(dat.index))))

    logging.debug('columns: %s'%(format(dat.columns)))
    return(dat)

def _clim(f,s):
    f['idx'] = f.index.strftime('%m%d%H%M')
    idx_time = sorted(set(f['idx']))
    c=pd.DataFrame({'month': [int(x[0:2]) for x in idx_time],
                    'day': [int(x[2:4]) for x in idx_time],
                    'hour': [int(x[4:6]) for x in idx_time],
                    'minute': [int(x[6:8]) for x in idx_time]})
    c.reset_index(drop=True, inplace=True)
    g=f.groupby('idx')[s]
    c['lo']=g.agg(np.nanmin).values
    c['ls']=g.agg(lambda x: np.nanpercentile(x.values,16)).values
    c['md']=g.agg(np.median).values
    c['mn']=g.agg(np.nanmean).values
    c['hs']=g.agg(lambda x: np.nanpercentile(x.values,84)).values
    c['hi']=g.agg(np.nanmax).values
    c[ 'n']=g.agg(lambda x: sum(~np.isnan(x.values))).values
    return c


def _climate_check(station:int):
    path = os.path.join(_CACHEDIR,_CLIMATEDB.format(station))
    if not os.path.exists(path):
        logging.debug('climate_check: db not found')
        modtime = _OLDEST
    elif not zipfile.is_zipfile(path):
        raise EnvironmentError('existing file is not db: %s'%path)
    else:
        db = zipfile.ZipFile(path, 'r')
        try:
            mod_sec = int(db.comment.decode())
        except ValueError:
            mod_sec = 0
        if mod_sec == 0:
            logging.debug('climate_check: db empty')
            modtime = _OLDEST
        else:
            logging.debug('climate_check: db has time set')
            modtime = pd.to_datetime(mod_sec * 1000000000)   # s -> ns
        db.close()
    return modtime

def _climate_write(station:int, data:pd.DataFrame, kind:str):
    if kind not in _KINDS:
        raise ValueError('unknown kind: %s'%kind)
    outputs = _OUTPUTS[kind]
    # db file to write
    path = os.path.join(_CACHEDIR,_CLIMATEDB.format(station))
    # move db to old-file name
    if os.path.exists(path):
        oldpath = path + '~'
        os.rename(path, oldpath)
    else:
        oldpath = None
    # create new empty db file
    with zipfile.ZipFile(path,'w') as db:
        # add new files
        for key,val in outputs.items():
            logging.info ('calculate "%s" from "%s"'%(key, val))
            clim = _clim(data, val)
            name = 'climate-%s-%s'%(kind, key)
            string = clim.to_csv(index=False,float_format='%7.2f')
            db.writestr(name, string)
        # make file in zip mode 644 = -rw-r--r--
        for x in db.filelist:
            x.external_attr = 0o644 << 16
        # now copy all other files from old to new db
        if oldpath:
            with zipfile.ZipFile(oldpath,'r') as old:
                for l in old.infolist():
                    if not l.filename in db.namelist():
                        db.writestr(l.filename, old.read(l))
            os.remove(oldpath)
        # store update time
        db.comment = format(pd.datetime.now(), '%s').encode()

def _climate_read(station:int, dates:list, kind:str, key:str):
    name = 'climate-%s-%s'%(kind, key)
    path = os.path.join(_CACHEDIR,_CLIMATEDB.format(station))
    logging.debug('opening db: %s'%path)
    with zipfile.ZipFile(path,'r') as db:
        logging.debug('loading table: %s'%name)
        f = db.read(name).decode()
        clim = pd.read_csv(StringIO(f))
    c_index = ['{:02d}{:02d}{:02d}{:02d}'.format(
            x['month'], x['day'], x['hour'], x['minute'])
            for x in clim.to_dict(orient="records")]
    d_index = ['{:02d}{:02d}{:02d}{:02d}'.format(
            x.month, x.day, x.hour, x.minute) for x in dates]
    re = pd.DataFrame(index=dates, columns=clim.columns)
    for i,di in zip(re.index,d_index):
        re.loc[i] = clim[[x == di for x in c_index]].values
    return re

def _check_for_updates(station:int):
    ftpfiles = {}
    for k in _KINDS:
        files = _ftp_list(station, k)
        ftpfiles.update(files)
    newest = _OLDEST
    for k,v in ftpfiles.items():
        if v['date'] > newest:
            newest = v['date']
    return newest


def _download_from_cdc(station:int, keep=True):
    for k in _KINDS:
        ftpfiles = _ftp_list(station, k)
        zipfiles = _ftp_download(ftpfiles, k)
        datafiles = _extract_hist(zipfiles, k)
        metafiles = _extract_meta(zipfiles)
        stationinfo = _read_meta(station, metafiles)
        dat = _read_hist(datafiles, k)
        dat = _data_contitioning(dat,
                                 stationinfo,
                                 k,
                                 lenyear=_LENYEAR,
                                 lastyear=_LASTYEAR,
                                 fastred=_FASTRED)
        _climate_write(station, dat, k)

    if not keep: _remove_files(zipfiles)
    _remove_files(datafiles)
    _remove_files(metafiles)

###############################################################################
#
#  public funktions
#
###############################################################################

def get_check_interval():
    '''
    return the interval at which is CDC server is checked for updated data
    
    :return: check interval
    :rtype: pandas.Timedelta
    '''
    return _CHECK_INTERVAL
def set_check_interval(value, unit):
    '''
    set the interval at which is CDC server is checket for updated data
    
    :param value: Timedelta, timedelta, np.timedelta64, str, or int
    :param unit: str, the unit of the input, if input is an integer, default ‘ns’
     Possible values: ‘W’, ‘D’, ‘T’, ‘S’, ‘L’, ‘U’, ‘N’, ‘days’ or ‘day’
     and all other values permitted by numpy, down to ‘ns’.
    '''
    this._CHECK_INTERVAL = pd.Timedelta(value, unit)

# -----------------------------------------------------------------------------

def get_cachedir():
    '''
    return the path of the directory where the cached statistics are stored
    
    :return: directory path
    :rtype: str
    '''
    return _CACHEDIR
def set_cachedir(path:str):
    '''
    set the path of the directory where the cached statistics are stored
    
    :param path: str, directory path
    
    The directory, including non-existent parent directories, is created upon
    first update after setting a new path.
    '''
    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.isdir(path) and os.access(path, os.R_OK | os.W_OK | os.X_OK ):
        this._CACHEDIR = path

# -----------------------------------------------------------------------------

def get_lenyear():
    '''
    return time period in years over which the statistcs are calculated
    
    :return: period length in years
    :rtype: int
    '''
    return _LENYEAR
def set_lenyear(lenyear:int):
    '''
    set the time period in years over which the statistcs are calculated
    
    :param lenyear: int, period length in years, must be >0, default is 30.
    '''
    if not isinstance(lenyear,int):
        lenyear = int(lenyear)
    if lenyear > 0:
        this._LENYEAR = lenyear
    else:
        raise ValueError('lenyear must be >0')

# -----------------------------------------------------------------------------

def get_lastyear():
    '''
    return the last year over which the statistcs are calculated
    
    :return: year
    :rtype: int
    '''
    return _LASTYEAR
def set_lastyear(lastyear):
    '''
    set the last year over which the statistcs are calculated
    
    :param lastyear: int, year, must less than current year, 
      default is last year.
    '''
    if lastyear is None:
        this._LASTYEAR = None
    else:
        if not isinstance(lastyear,int):
            lastyear = int(lastyear)
        if lastyear < pd.datetime.now().year:
            this._LASTYEAR = lastyear
        else:
            raise ValueError('lastyear must less than current year')

# -----------------------------------------------------------------------------

def update(station, key:str, kind:str, force=False):
    '''
    check for updated data on the server 
    and refresh statistics if new data are available
    
    :param station: int, DWD number of station
    :param key: str, value to put out
    :param kind: str, one of 'hourly', 'daily', or 'monthly'
    :param force: bool, `True` means to download data an  refresh statistics,
      unconditionally. Default is `False`
    '''
    
    # check attributes
    if kind not in _KINDS:
        raise ValueError('unknown kind: %s'%kind)
    if not key in _OUTPUTS[kind].keys():
        raise ValueError('unknown key: %s'%key)

    # get time of last update (or db is empty)
    modtime = _climate_check(station)
    logging.info('database for station %05i created: %s'%(station,format(modtime)))
    # check if it is time to look for new data at cdc
    if force or modtime + _CHECK_INTERVAL <= pd.datetime.now():
        logging.info('checking for updxated data on server')
        # get latest modfication time at cdc:
        newest = _check_for_updates(station)
        logging.info('data for station %05i last updated: %s'%(station,format(newest)))

        if force or newest > modtime:
            # get new data and extract climate data
            logging.info('downloading data for station %05i'%(station))
            _download_from_cdc(station)

    return

# -----------------------------------------------------------------------------

def fetch(station, dates, key:str, kind:str):
    '''
    return statistics for `station` at `dates` for variable `key`,
    calculated ofer `kind`. 
    Check for updated data before, 
    if cached statistics have reache a certain age.
    
    :param station: int, DWD number of station
    :param dates: list or list-like of pandas.Datetime 
      or objects that can be converted to  pandas.Datetime,
      return statistics matchin each date
    :param key: str, value to put out
    :param kind: str, one of 'hourly', 'daily', or 'monthly'
    
    :return: statistics (minimum, lower quartile, median, 
      mean, upper quarteile, maximum) for each date
    :rtype: pandas.DataFrame
    '''
    # check attributes
    if kind not in _KINDS:
        raise ValueError('unknown kind: %s'%kind)
    if not key in _OUTPUTS[kind].keys():
        raise ValueError('unknown key: %s'%key)
    if not pd.api.types.is_list_like(dates):
        dates = [dates]
    if not pd.api.types.is_datetime64tz_dtype(dates):
        try:
            dates = pd.to_datetime(dates, utc=True)
        except:
            raise ValueError('dates cannot be converted to datetime')

    update(station, key, kind)

    data = _climate_read(station, dates, kind, key)

    return data

###############################################################################
#
#  init module
#
###############################################################################

logging.basicConfig(level=logging.DEBUG)

set_cachedir(_CACHEDIR)

if __name__=='__main__':
    a = fetch(5100,
              pd.date_range('2022-06-01', '2022-06-02', freq='1H'),
              't',
              'hourly'
              )
    print(a)