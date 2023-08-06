'''
Created on Jun 29, 2017

@author: Andrew
'''
from allRoomsModule import AllRooms


class Connector(object):
    '''
    classdocs
    '''

    def __init__(self, line):
        '''
        Constructor
        '''
        tokens = line.split(',')
#        print ('Tokens:', tokens)
        self.ID = tokens[0]
        self.floor = int(tokens[1])
        self.r1 = AllRooms.clsGetRoom (tokens[2])
#        print('Room1:', self.r1)
        self.r2 = AllRooms.clsGetRoom (tokens[3])
#        print('Room2:', self.r2)
        dOrG = tokens[4]
        if dOrG == 'D':
            self.dOrG = True
        else:
            self.dOrG = False
        self.x = int(tokens[5])
        self.y = int(tokens[6])
        self.colspan = int(tokens[7])
        self.rowspan = int(tokens[8][0])
        self.orientation = tokens[9][0]
        self.state = False

    def isItDoor(self):
        return self.dOrG

    def isDoorOpen(self):
        return self.state

    def toggleDoor(self):
        self.state = not self.state
        return self.dOrG

    def getOtherRoom (self, room):
        r1ID = self.r1.getID ()
        r2ID = self.r2.getID()
        roomID = room.getID()

        if r1ID == roomID:
            return self.r2
        elif r2ID == roomID:
            return self.r1
        else:
            print('OOOPS')
            exit()

    def getID(self):
        return self.ID