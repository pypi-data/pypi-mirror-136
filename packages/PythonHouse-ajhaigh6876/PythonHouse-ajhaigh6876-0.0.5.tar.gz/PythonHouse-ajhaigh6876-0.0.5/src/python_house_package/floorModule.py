'''
Created on Jun 29, 2017

@author: Andrew
'''
from allRoomsModule import AllRooms
from roomModule import Room


class Floor(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
#        print ('inside Floor __init__')
        self.rooms = {}


    def setupRoom(self, line):
        tokens = line.split(',')
        ID = tokens[0]
        floorNumber = int(tokens[1])
        x = int(tokens[2])
        y = int(tokens[3])
        name = tokens[4]
        room = Room (ID, floorNumber, name, x, y)
#        print ('Room: ', room, ID, floorNumber, name, x, y)
        self.rooms[name]=room
        AllRooms.clsAddRoom(room)
        north = tokens[5]
        if north != "0":
            room.setConnection (room.NORTH, north)
        east = tokens[6]
        if east != "0":
            room.setConnection (room.EAST, east)
        south = tokens[7]
        if south != "0":
            room.setConnection (room.SOUTH, south)
        if len(tokens [8]) == 2:
            west = tokens[8][0]
        else:
            west = tokens[8][0] + tokens[8][1]
        if west != "0":
            room.setConnection (room.WEST, west)
