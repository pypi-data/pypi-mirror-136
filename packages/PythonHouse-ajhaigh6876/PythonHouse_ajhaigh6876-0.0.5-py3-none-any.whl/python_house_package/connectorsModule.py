'''
Created on Jun 29, 2017

@author: Andrew
'''
from connectorModule import Connector


class Connectors():
    '''
    classdocs
    '''
    connectorsKV = {}

    def __init__(self):
        '''
        Constructor
        '''
#        print ('hello from the Connectors __init__')

    def setupConnector (self, line):
#        print ('inside setupConnector')
        tokens = line.split(',')
        ID = tokens[0]
        connector = Connector (line)
#        print ('Connector: ', connector, ID)
        Connectors.connectorsKV[ID]=connector

