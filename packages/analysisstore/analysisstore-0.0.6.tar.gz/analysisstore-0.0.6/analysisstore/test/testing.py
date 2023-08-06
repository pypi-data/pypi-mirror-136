from pymongo import MongoClient
import time as ttime
import uuid
import requests
import ujson
from subprocess import Popen
import os
import pytest


TESTING_CONFIG = dict(host='localhost', port=7601,
                      timezone='US/Eastern', serviceport=7601,
                      database='astoretest{0}'.format(str(uuid.uuid4())),
                      mongohost='localhost',
                      mongoport=27017)


def astore_setup():
    f = os.path.dirname(os.path.realpath(__file__))
    proc = Popen(["python", "../../startup.py", "--mongo-host",
                  TESTING_CONFIG["mongohost"],
                                 "--mongo-port",
                                 str(TESTING_CONFIG['mongoport']),
                                 "--database", TESTING_CONFIG['database'],
                                 "--timezone", TESTING_CONFIG['timezone'],
                                 "--service-port",
                                 str(TESTING_CONFIG['serviceport'])], cwd=f)
    ttime.sleep(1.3) # make sure the process is started
    return proc


def astore_teardown(proc):
    proc2 = Popen(['kill', '-9', str(proc.pid)])
    ttime.sleep(5) # make sure the process is killed
    conn = MongoClient(host=TESTING_CONFIG['mongohost'],
                       port=TESTING_CONFIG['mongoport'])
    conn.drop_database(TESTING_CONFIG['database'])
    print('\nTearing down the server and dropping the db\n')
    ttime.sleep(1.3)
