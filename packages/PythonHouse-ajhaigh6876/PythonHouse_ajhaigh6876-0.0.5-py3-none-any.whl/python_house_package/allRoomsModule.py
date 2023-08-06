'''
Created on Jun 29, 2017

@author: Andrew
'''
#from roomModule import Room

class AllRooms():
    '''
    classdocs
    '''
    allRoomsKV = {}

    def __init__(self):
        '''
        Constructor
        '''
#        print ('hello from the AllRooms __init__')

    @classmethod
    def clsAddRoom (cls, room):
        cls.allRoomsKV[room.ID] = room

    @classmethod
    def clsGetRoom (cls, ID):
        return cls.allRoomsKV[ID]
    
