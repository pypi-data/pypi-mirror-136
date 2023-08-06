'''
Created on Jun 28, 2017

@author: Andrew
'''
import sys

from connectorsModule import Connectors
from displayModule import Display
from floorsModule import Floors
from personModule import Person


#print (sys.path)
class House():
    '''
    classdocs
    '''
    numFloors = 0
    width = 0
    depth = 0
    display = Display ()
    floors = Floors ()
    connectors = Connectors ()
    direction = ''

    def __init__(self):
        '''
        Constructor
        '''
        #self.display.enterRomm ()

    def setupHouse(self, line):
        tokens = line.split(',')
        House.numFloors = tokens[1]
        House.width = tokens[2]
        House.depth = tokens[3][0]
#        print('pre-createFloors')
        House.floors.createFloors (int(House.numFloors))

    def setupRoom (self, line):
#        print("pre-setupRoom")
        House.floors.setupRoom (line)

    def setupConnector (self, line):
#        print("pre-setupConnector")
        House.connectors.setupConnector (line)

    def setupFirstRoom(self,line):
        tokens=line.split(',')
#        ID = tokens[0]
        floorNumber = tokens[1]
        name = tokens[2]
        House.direction=tokens[3]
        floors = Floors.floorsKV
        floor = floors['F' + floorNumber]
        currentRoom = floor.rooms[name]
        Person(currentRoom, House.direction)

    def setup(self):
#        with open ('f:\\eclipse_personal\\PythonHouse\\house.txt') as text_file:
        with open ('house.txt') as text_file:
            while 1:
                line = text_file.readline()
                if not line:
                    break
                else:
                    # print(line)
#                    print(line[0])
                    if '/' in line:
                        continue
                    elif 'H' in line[0]:
#                        print('found House')
                        self.setupHouse (line)
                    elif 'R' in line[0]:
#                        print('found roomModule')
                        self.setupRoom(line)
                    elif 'C' in line[0]:
#                        print('found Connector')
                        self.setupConnector(line)
                    elif 'S' in line[0]:
                        print('found Start')
                        self.setupFirstRoom(line)
                    else:
                        print('no comment')
            text_file.close()
            House.display.setup(int(House.numFloors), int(House.width), int(House.depth))

if __name__== '__main__':
    house = House ()
    house.setup ()
    House.display.enterRoom ()
    House.display.app.go()

