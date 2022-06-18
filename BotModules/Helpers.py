from itertools import izip as zip, count # izip for maximum efficiency
import re, sqlite3, time, os, datetime, pandas as pd
pd.set_option('display.width', 1000)
class HelperClass():

    def __init__(self):
        pass

    def save_log(self, id, msg):
        f = open('logs/log_'+str(id)+'.txt', 'a+')
        msg = '[' + datetime.datetime.fromtimestamp(time.time()).strftime('%d-%b-%y %I:%M:%S %p') + ']: ' + msg
        f.write(msg+'\n')
        f.close()

    def read_log(self, id):
        if os.path.exists('logs/log_' + str(id)+'.txt'):
            f = open('logs/log_'+str(id)+'.txt', 'r')
            msg = f.readlines()
            f.close()
            return msg
        else:
            return ''

    def delete_log(self, id):
        if os.path.exists('logs/log_' + str(id)+'.txt'):
            os.remove('logs/log_' + str(id)+'.txt')
            return 'Log deleted!'
        else:
            return 'File not found!'


def begins_with(string, l):
    pos = []
    res = [s for s in l if str(string) in s]
    for r in res:
        pos.append([[i,j.replace('\n','')] for i, j in zip(count(), l) if j == r][0])
    return pos


def save_file(filename, l):
    f = open(filename, 'w')
    for i in range(0, len(l)):
        f.write(l[i])
    f.close()

def to_db(dataframe, db_table, db_conn, log_file):
    # Data doesn't exist. Store the log data
    dataframe = dataframe.copy()
    dataframe['log_file'] = log_file
    dataframe['timestamp'] = int(time.time())
    dataframe.to_sql(db_table,
                     con=db_conn,
                     if_exists='append',
                     index=None)
    print('Data written to table!')
    
def GetHumanReadable(size,precision=2):
    suffixes=[' B',' KB',' MB',' GB',' TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1
        size = size/1024.0
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])
def GetHumanReadable1(size,precision=2):
    suffixes=[' Bytes',' Kbps',' Mbps',' Gbps',' Tbps']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1
        size = size/1024.0
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])

########

