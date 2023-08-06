'''
Created on Jun 29, 2017

@author: Andrew
'''
from appJar import gui

from connectorsModule import Connectors
from floorsModule import Floors
from personModule import Person
from roomModule import Room


#from connectorModule import Connector
class Display():
    '''
    classdocs
    '''
    app = gui('House')

    def __init__(self):
        '''
        Constructor
        '''    
#        print ('inside Display __init__')

    def logoutFunction(self):
        return Display.app.yesNoBox("Confirm Exit", "Are you sure you want to exit?")

    def moveForwards(self):
        valid = self.leaveRoom()
        if valid:
            self.enterRoom()
 
    def pressBtn (self, btn):
        if btn == "Forwards":
            print('Forwards')
            self.leaveRoom()
            self.enterRoom()
        elif btn == "Left":
            print('Left')
            self.rotateLeft()
        elif btn == 'Right':
            print('Right')
            self.rotateRight()
        elif btn == 'Turn Around':
            print ('Turn Around')
            self.rotate180()
        elif btn == 'Toggle':
            print ('Toggle')
            self.toggleDoors()

    def setup(self, numFloors, width, depth):

        floorsKV = Floors.floorsKV
        
        for findex in range (numFloors, 0, -1):
#            print ('findex', findex)
            Display.app.startLabelFrame('Floor ' + str(findex))
            Display.app.setSticky('news')
            Display.app.setExpand('both')

            floor = floorsKV['F' + str(findex)]
#            print ('Floor: ', floor)
#            print ('Floor Rooms: ', floor.rooms)
            for roomKey in floor.rooms:
#                print('Key  : ', roomKey)
#                print('Value: ', floor.rooms[roomKey])
                room = floor.rooms[roomKey]
                x = room.x
                y = room.y
                floorNumber = room.floor
                title = 'R' + str(floorNumber) + str(x) + str(y)
#                print (room.ID, x, y, 2,2)
                Display.app.addImage(title, 'houseOff.gif', column=x, row=y, colspan=2, rowspan=2)
#                Display.app.setLabelBg(title, "blue")
#                app.addImage(title, "houseNext.gif", y, x, 2, 2)
            for connectorKey in Connectors.connectorsKV:
                connector = Connectors.connectorsKV[connectorKey]
#                print('Connector: ', connector)
                if connector.floor == findex:
                    cx = connector.x
                    cy = connector.y
                    cc = connector.colspan
                    cr = connector.rowspan
                    if connector.isItDoor():
                        Display.app.addImage(connector.ID, 'houseDoorClosed.gif', column=cx, row=cy,
                            colspan=cc, rowspan=cr)
                    else:
                        if connector.orientation == 'H':
                            Display.app.addImage(connector.ID, 'houseNotDoorH.gif', column=cx, row=cy,
                                                 colspan=cc, rowspan=cr)
                        else:
                            Display.app.addImage(connector.ID, 'houseNotDoorV.gif', column=cx, row=cy,
                                                 colspan=cc, rowspan=cr)

#                    print(connector.ID, cx, cy, cc, cr)
#                    Display.app.setIconBg(connector.ID, "red")
            Display.app.stopLabelFrame ()
        
        Display.app.startLabelFrame('Moverment')
        Display.app.setSticky('news')
        Display.app.setExpand('both')
        Display.app.addButtons(["Forwards"], self.pressBtn, 0, 0, 3, 1)
        Display.app.addButtons(["Left","Toggle","Right"], self.pressBtn, 1, 0, 3, 1)
        Display.app.addButtons(["Turn Around"], self.pressBtn, 2, 0, 3, 1)
        Display.app.addLabel('Number','',3,0,3,1)
        Display.app.addLabel('Room','',4,0,3,1)
        Display.app.stopLabelFrame()

        Display.app.bindKey ('8', self.moveForwardsEvent)
        Display.app.bindKey ('4', self.rotateLeftEvent)
        Display.app.bindKey ('5', self.toggleDoorsEvent)
        Display.app.bindKey ('6', self.rotateRightEvent)
        Display.app.bindKey ('2', self.rotate180Event)

#        Display.app.bindKey ('<Up>', self.moveForwardsEvent)
#        Display.app.bindKey ('<Left>', self.rotateLeftEvent)
#        Display.app.bindKey ('<space>', self.toggleDoorsEvent)
#        Display.app.bindKey ('<Right>', self.rotateRightEvent)
#        Display.app.bindKey ('<Down>', self.rotate180Event)

        Display.app.bindKey ('x', Display.app.stop)
        Display.app.setStopFunction(self.logoutFunction)
#        Display.app.go()

    def enterRoom(self):
        person = Person.getPerson()
        room = person.getCurrentRoom()
#        direction = person.getDirection()
        Display.app.setLabel('Number', room.getFloor())
        Display.app.setLabel('Room', room.getName())
        self.setupRoom(person, room)
        for index in range (4):
            if room.getConnection(index) != '0':
                connName = room.getConnection(index)
                print('Connection Name(%s): %s' % (str(index), connName))
                conn = Connectors.connectorsKV[connName]
                person.setRoom(index, None)
                if conn.isItDoor():
                    if conn.isDoorOpen():
                        nextRoom = conn.getOtherRoom(room)
                        person.setRoom(index,nextRoom)
                        floor = nextRoom.getFloor()
                        x = nextRoom.x
                        y = nextRoom.y
                        title = 'R' + str(floor) + str(x) + str(y)
                        print('Modify Room - Entered', nextRoom.getName())
                        Display.app.setImage(title,'houseNext.gif')
                else:
                    nextRoom = conn.getOtherRoom(room)
                    person.setRoom(index,nextRoom)
                    floor = nextRoom.getFloor()
                    x = nextRoom.x
                    y = nextRoom.y
                    title = 'R' + str(floor) + str(x) + str(y)
                    print('Modify Room - Entered', nextRoom.getName())
                    Display.app.setImage(title,'houseNext.gif')

    def leaveRoom(self):
        person = Person.getPerson()
        room = person.getCurrentRoom()
        if room.getConnection(person.getDirection()) != '0':
            connName = room.getConnection(person.getDirection())
            print('Connection Name(%s): %s' % (str(person.getDirection()), connName))
            conn = Connectors.connectorsKV[connName]
            if conn.isItDoor():
                if not conn.isDoorOpen():
                    return False

        if person.getDirection() == Room.NORTH:
            if person.getRoom(Room.NORTH) != None:
                person.setCurrentRoom(person.getRoom(Room.NORTH))
        elif person.getDirection() == Room.EAST:
            if person.getRoom(Room.EAST) != None:
                person.setCurrentRoom(person.getRoom(Room.EAST))
        elif person.getDirection() == Room.SOUTH:
            if person.getRoom(Room.SOUTH) != None:
                person.setCurrentRoom(person.getRoom(Room.SOUTH))
        elif person.getDirection() == Room.WEST:
            if person.getRoom(Room.WEST) != None:
                person.setCurrentRoom(person.getRoom(Room.WEST))
        for index in range (4):
            if person.getRoom(index) != None:
                nextRoom = person.getRoom(index)
                floor = nextRoom.getFloor()
                x = nextRoom.x
                y = nextRoom.y
                title = 'R' + str(floor) + str(x) + str(y)
                print('Modify Room - adjacent', nextRoom.getName())
                Display.app.setImage(title,'houseOff.gif')
        return True

    def toggleDoors(self):
        person = Person.getPerson()
        room = person.getCurrentRoom()
        direction = person.getDirection()
        for index in range (4):
            if index != direction:
                continue
            if room.getConnection(index) != '0':
                connName = room.getConnection(index)
                print('Connection Name(%s): %s' % (str(index), connName))
                conn = Connectors.connectorsKV[connName]
                person.setRoom(index, None)
                if conn.isItDoor():
                    conn.toggleDoor()
                    nextRoom = conn.getOtherRoom(room)
                    person.setRoom(index,nextRoom)
                    floor = nextRoom.getFloor()
                    x = nextRoom.x
                    y = nextRoom.y
                    title = 'R' + str(floor) + str(x) + str(y)
                    if conn.isDoorOpen():
                        print('Modify Room - visible', nextRoom.getName())
                        Display.app.setImage(title,'houseNext.gif')
                        Display.app.setImage(conn.getID(),'houseDoorOpen.gif')
                    else:
                        print('Modify Room - hidden', nextRoom.getName())
                        Display.app.setImage(title,'houseOff.gif')
                        Display.app.setImage(conn.getID(),'houseDoorClosed.gif')
                else:
                    nextRoom = conn.getOtherRoom(room)
                    person.setRoom(index,nextRoom)
                    floor = nextRoom.getFloor()
                    x = nextRoom.x
                    y = nextRoom.y
                    title = 'R' + str(floor) + str(x) + str(y)
                    print('Modify Room - visible2', nextRoom.getName())
                    Display.app.setImage(title,'houseNext.gif')

    def setupRoom(self, person, room):
        direction = person.getDirection()
        x = room.x
        y = room.y
        if direction == Room.NORTH:
            title = 'R' + str(room.getFloor()) + str(x) + str(y)
            print('Modify:with Forwards arraw', title)
            Display.app.setImage(title,'houseN.gif')
        if direction == Room.EAST:
            title = 'R' + str(room.getFloor()) + str(x) + str(y)
            print('Modify:with RIGHT arraw', title)
            Display.app.setImage(title,'houseE.gif')
        if direction == Room.SOUTH:
            title = 'R' + str(room.getFloor()) + str(x) + str(y)
            print('Modify:with Turn Around arraw', title)
            Display.app.setImage(title,'houseS.gif')
        if direction == Room.WEST:
            title = 'R' + str(room.getFloor()) + str(x) + str(y)
            print('Modify:with LEFT arraw', title)
            Display.app.setImage(title,'houseW.gif')

    def rotateLeft (self):
        person = Person.getPerson()
        room = person.getCurrentRoom()
        person.rotateLeft()
        self.setupRoom(person,room)

    def rotateRight (self):
        person = Person.getPerson()
        room = person.getCurrentRoom()
        person.rotateRight()
        self.setupRoom(person,room)

    def rotate180 (self):
        person = Person.getPerson()
        room = person.getCurrentRoom()
        person.rotate180()
        self.setupRoom(person,room)

    def moveForwardsEvent(self, event):
        print('MoveForwards')
        self.moveForwards()

    def rotateLeftEvent(self,event):
        print('RotateLeftEvent')
        self.rotateLeft()

    def rotateRightEvent(self,event):
        print('RotateRightEvent')
        self.rotateRight()

    def rotate180Event(self,event):
        self.rotate180()

    def toggleDoorsEvent(self,event):
        self.toggleDoors()
