'''
Created on Jun 29, 2017

@author: Andrew
'''
from math import floor


class Room ():
    '''
    classdocs
    '''
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def __init__(self, ID, floorNumber, name, x, y):
        '''
        Constructor
        '''
        self.ID = ID
        self.floor = int(floorNumber)
        self.name = name
        self.__x = int(x)
        self.__y = int(y)
        self.connections = ['0','0','0','0']
#        print ('Inside Room:', self.ID, self.floor, self.name, self.x, self.y)

    def setConnection (self, side, connection):
        self.connections[side] = connection

    def getConnection (self, side):
        return self.connections[side]

    def getFloor (self):
        return self.floor

    def getFloorNumber(self):
        return self.floor

    def getID(self):
        return self.ID

    def getName(self):
        return self.name

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        # can validate before assigning
        self.__x = x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        # can validate before assigning
        self.__y = y
