'''
Created on Jun 29, 2017

@author: Andrew
'''
from roomModule import Room


#from allRoomsModule import AllRooms
class Person(object):
    '''
    classdocs
    '''

    def __init__(self, currentRoom, direction):
        '''
        Constructor
        '''
        self.currentRoom = currentRoom
        self.rooms = [None]*4
        if direction == 'N':
            self.direction = Room.NORTH
        if direction == 'E':
            self.direction = Room.EAST
        if direction == 'S':
            self.direction = Room.SOUTH
        if direction == 'W':
            self.direction = Room.WEST
        Person.me = self

    def setCurrentRoom(self, currentRoom):
        self.currentRoom = currentRoom

    def getCurrentRoom (self):
        return self.currentRoom

    def getDirection(self):
        return self.direction

    def setRoom (self, direction, room):
        self.rooms[direction] = room

    def getRoom (self,direction):
        return self.rooms[direction]

    def rotateLeft(self):
        self.direction = self.direction - 1
        if self.direction == -1:
            self.direction = 3

    def rotateRight(self):
        self.direction = self.direction + 1
        if self.direction == 4:
            self.direction = 0

    def rotate180(self):
        self.direction = self.direction + 2
        if self.direction == 4:
            self.direction = 0
        if self.direction == 5:
            self.direction = 1

    @classmethod
    def getPerson(cls):
        return cls.me
