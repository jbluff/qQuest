import os
import datetime

import dill
import pygame

from qQuest import constants
from qQuest import graphics
from qQuest.qqGlobal import CLOCK, GAME 

DATETIME_FORMAT = '%Y%m%d%H%M%S'
SAVEPATH = os.path.join(os.path.dirname(__file__),"..","saves")

#Todo:  make MenuListItem class
# selected or not
# selectable or not

class Menu:
    def __init__(self, parentSurface, menuSize=(300,200)):
        self.parentSurface = parentSurface
        self.menuWidth, self.menuHeight = menuSize

        windowWidth = constants.CELL_WIDTH*GAME.mapWidth
        windowHeight = constants.CELL_HEIGHT*GAME.mapHeight

        self.coordY = (windowHeight-self.menuHeight)/2
        self.coordX = (windowWidth-self.menuWidth)/2
        
        self.menuSurface = pygame.Surface((self.menuWidth, self.menuHeight))

        self.breakLoop = False
        self.redrawGame = True

        self.mainLoop()

    def mainLoop(self):
        
        while not self.breakLoop:
            self.restartLoop()

            eventsList = pygame.event.get()
            for event in eventsList:
                self.parseEvent(event)

            self.finishLoop()

            # Do we need to redraw the main game surface?
            if self.redrawGame:
                graphics.drawGame(fovMap=GAME.player.fovMap)
                redrawGame = False

            self.redrawMenu()

    def redrawMenu(self):
        self.redrawMenuBody()
        self.parentSurface.blit(self.menuSurface, (self.coordX, self.coordY))
        CLOCK.tick(constants.GAME_FPS)
        pygame.display.flip()

    '''
    How to respond to key strokes
    '''
    def parseEvent(self, event):
        raise NotImplementedError("parseEvent must be implemented by child class")

    '''
    What do before the input parsing
    '''
    def restartLoop(self):
        raise NotImplementedError("restartLoop must be implemented by child class")

    '''
    What to do after input parsing
    '''
    def finishLoop(self):
        raise NotImplementedError("finishLoop must be implemented by child class")

    '''
    What gets drawn on the menu surface
    '''
    def redrawMenuBody(self):
        raise NotImplementedError("redrawMenuBody must be implemented by child class")

# This is a rather pointless thing, at present.
class PauseMenu(Menu):
    def __init__(self, parentSurface):
        super().__init__(parentSurface, menuSize=(200,50))

    def restartLoop(self):
        pass

    def finishLoop(self):
        pass

    def parseEvent(self, event):
        if event.type != pygame.KEYDOWN:
            return
                    
        if event.key == pygame.K_q:
            self.breakLoop = True

    def redrawMenuBody(self):
        graphics.drawTextList(self.menuSurface, [["P is for Paused",constants.COLOR_WHITE]])

class TextListMenu(Menu):
    def __init__(self, parentSurface):
        self.selected = 0
        super().__init__(parentSurface)

    def initTextList(self):
        raise NotImplemented("initTextList must be overwritten by children")

    def restartLoop(self):
        self.initTextList()
        self.updateSelected() #this really only needs to be called in the init
        self.menuSurface.fill(constants.COLOR_BLACK) # this shouldn't really be here.

    def updateSelected(self):
        for idx, el in enumerate(self.textList):
            if idx == self.selected:
                self.textList[idx][1] = constants.COLOR_RED
            else:
                self.textList[idx][1] = constants.COLOR_GREY

    def decrementSelected(self):
        if self.selected > 0:
            self.selected -= 1
        self.updateSelected()

    def incrementSelected(self):
        if self.selected < len(self.textList) - 1:
            self.selected += 1
        self.updateSelected()

    def redrawMenuBody(self):
        graphics.drawTextList(self.menuSurface, self.textList)

    def finishLoop(self):
        pass

    def parseEvent(self, event):
        if event.type != pygame.KEYDOWN:
            return 'continue'
                    
        if event.key == pygame.K_q:
            self.breakLoop = True
            return ''

        if event.key == pygame.K_DOWN:
            self.incrementSelected()
            return 'continue'

        elif event.key == pygame.K_UP:
            self.decrementSelected()      
            return 'continue'

class SaveLoadMenu(TextListMenu):
    def initTextList(self):
        self.textList = [["Save", constants.COLOR_WHITE],["Load", constants.COLOR_WHITE]]
 
    def parseEvent(self, event):
        ret = super().parseEvent(event)
        if ret == 'continue':
            return None

        if event.key == pygame.K_RETURN:
            if self.selected == 0:
                self.gameSave()

            if self.selected == 1:
                LoadMenu(self.parentSurface)
                self.breakLoop = True


    def gameSave(self, saveName='default'):
        dt = datetime.datetime.now()
        dtString = dt.strftime(DATETIME_FORMAT)

        fileName = dtString + '_' + saveName + '.sav'
        filePath = os.path.join(SAVEPATH,fileName)
        print(filePath)
        with open(filePath, 'wb') as f:
            dill.dump(GAME, f)
        pass

class InventoryMenu(TextListMenu):
    def __init__(self, parentSurface, actor):
        self.actor = actor
        self.selected = 0
        super().__init__(parentSurface)

    def initTextList(self):
        self.textList = [["Inventory:", constants.COLOR_WHITE],]
        self.textList.extend([[obj.name,constants.COLOR_GREY] for obj in self.actor.container.inventory if not obj.deleted])

    def parseEvent(self, event):
        ret = super().parseEvent(event)
        if ret == 'continue':
            return None

        if len(self.textList) == 1: #empty inventory
            return 

        elif event.key == pygame.K_d:
            print('dropping')
            self.actor.container.inventory[self.selected-1].drop() #fix this nonsense.
            del self.textList[self.selected]
            self.decrementSelected()
            self.redrawGame = True

        elif event.key == pygame.K_u:
            invObj = self.actor.container.inventory[self.selected-1] # selected item's Actor.
            
            success = invObj.use(self.actor)
            if success:
                GAME.addMessage(self.actor.name + " uses " + invObj.name )
                if invObj.deleted:
                    del self.textList[self.selected] #delete from menu list -- doesn't really work.
                    self.decrementSelected()
            self.redrawGame = True

class LoadMenu(TextListMenu):
    def initTextList(self):
        allFiles = listSavedGames()

        self.textList = [[f, constants.COLOR_WHITE] for f in allFiles]
 
    def parseEvent(self, event):
        ret = super().parseEvent(event)
        if ret == 'continue':
            return None

        if event.key == pygame.K_RETURN:
            fname = self.textList[self.selected][0]
            print(f'loading {fname}')
            loadGame(fname)
            self.breakLoop = True

def loadGame(fname):
    global GAME

    filePath = os.path.join(SAVEPATH,fname)
    print(filePath)
    with open(filePath, 'rb') as f:
        newGame = dill.load(f)
    
    GAME.levels = newGame.levels
    GAME.currentLevelIdx = newGame.currentLevelIdx
    GAME.player = newGame.player
    GAME.messageHistory = newGame.messageHistory
    GAME.viewer = newGame.viewer

def listSavedGames():
    #datetime.strptime(date_string, format).
    saveFiles = []
    for f in os.listdir(SAVEPATH):
        name = os.path.join(SAVEPATH, f)
        if not os.path.isfile(name):
            continue
        if name.endswith(".sav"):
            saveFiles.append(f)
    return saveFiles
