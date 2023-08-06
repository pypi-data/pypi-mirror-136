'''
Created on Jun 29, 2017

@author: Andrew
'''
from floorModule import Floor


class Floors():
    '''
    classdocs
    '''
    floorsKV = {}

    def __init__(self):
        '''
        Constructor
        '''
#        print ('hello from the Floors __init__')

    def createFloors (self, number):
#        print ('inside createFloors')
        for index in range(number):
            floor = Floor()
#            print ('New Floor Object: ', floor)
            Floors.floorsKV['F' + str(index+1)] = floor

    def setupRoom (self, line):
#        print ('inside setupRoom')
        tokens = line.split(',')
        floorNumber= tokens[1]
#        print('Floor number: ', floorNumber)
        floor = self.floorsKV['F' + floorNumber]
#        print ('Floor: ', floor)
        floor.setupRoom(line)
#        print ('Floor rooms: ', floor.rooms)

    def getFloor (self, floorName):
        return Floors.floorsKV[floorName]
