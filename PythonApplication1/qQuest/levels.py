from qQuest import map_util

class Level:
    def __init__(self, parentGame, levelDict): #, fovMap):
        self.game = parentGame
        self.levelDict = levelDict
        self.currentMap = map_util.loadLevel(levelDict)

        self.fovMap = None
        #self.fovMap = []  ## TODO:  need to add ability to save FovMap when switching back to previous level

        self.currentObjects = []

    def checkForCreature(self, x, y, exclude_object = None):
        '''
        Returns target creature instance if target location contains creature
        '''
        target = None
        for obj in self.currentObjects:
            if (obj is not exclude_object and
                obj.x == x and #sub objectAtCoords into here
                obj.y == y and
                obj.creature):
                return obj
        return None

    def objectsAtCoords(self,x,y):
        return [obj for obj in self.currentObjects if obj.x == x and obj.y == y]