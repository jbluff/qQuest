import os
import datetime

import dill
import pygame

from qQuest import constants
from qQuest import graphics
from qQuest.game import CLOCK, GAME 

DATETIME_FORMAT = '%Y%m%d%H%M%S'
SAVEPATH = os.path.join(os.path.dirname(__file__),"..","saves")

#Todo:  make MenuListItem class
# selected or not
# selectable or not
class MenuListItem():
    def __init__(self, text,
                       textColorUnsel=constants.COLOR_WHITE, 
                       bgColorUnsel=constants.COLOR_BLACK, 
                       selectable=True, 
                       textColorSel=constants.COLOR_RED, 
                       bgColorSel=constants.COLOR_DGREY,
                       selected=False):
        self.text = text
        self.textColorUnsel = textColorUnsel
        self.bgColorUnsel = bgColorUnsel
        self.selectable = selectable
        self.textColorSel = textColorSel
        self.bgColorSel = bgColorSel
        self.selected = selected

class Menu:
    def __init__(self, parentSurface, menuSize=(300,200)):
        ''' Menu size is (x,y) in pixels '''

        self.parentSurface = parentSurface
        self.menuWidth, self.menuHeight = menuSize
        self.menuSurface = pygame.Surface((self.menuWidth, self.menuHeight))

        self.calculateDrawPosition()
               
        self.breakLoop = False
        self.redrawGame = True

        self.mainLoop()

    def calculateDrawPosition(self):
        windowWidth = constants.CELL_WIDTH*constants.CAMERA_WIDTH
        windowHeight = constants.CELL_HEIGHT*constants.CAMERA_HEIGHT
        self.coordY = (windowHeight-self.menuHeight)/2
        self.coordX = (windowWidth-self.menuWidth)/2

    def mainLoop(self):
        
        while not self.breakLoop:
            self.restartLoop()

            eventsList = pygame.event.get()
            for event in eventsList:
                self.parseEvent(event)

            self.finishLoop()

            if self.redrawGame:
                graphics.drawGame()#fovMap=GAME.viewer.fovMap)
                redrawGame = False

            self.redrawMenu()

    def redrawMenu(self):
        self.redrawMenuBody()
        self.parentSurface.blit(self.menuSurface, (self.coordX, self.coordY))
        CLOCK.tick(constants.GAME_FPS)
        pygame.display.flip()

    
    def parseEvent(self, event):
        ''' How to respond to key strokes '''
        raise NotImplementedError("parseEvent must be implemented by child class")

    def restartLoop(self):
        ''' What do before the input parsing '''
        raise NotImplementedError("restartLoop must be implemented by child class")

    def finishLoop(self):  
        ''' What to do after input parsing '''
        raise NotImplementedError("finishLoop must be implemented by child class")

    def redrawMenuBody(self):
        ''' What gets drawn on the menu surface '''
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
        graphics.drawTextList(self.menuSurface, [["P is for Paused",constants.COLOR_WHITE,constants.COLOR_BLACK]])

class TextListMenu(Menu):
    def __init__(self, parentSurface):
        self.selected=None
        self.initTextList()
        super().__init__(parentSurface)

    def initTextList(self):
        raise NotImplemented("sinitTextList must be overwritten by children")

    def restartLoop(self):
        pass
    
    @property
    def numSelectable(self):
        ''' how many selectable objects are in the menu? '''
        return sum([entry.selectable for entry in self.textList])

    def addItem(self, text, **kwargs):
        ''' Add an entry to the text list menu'''
        newEntry = MenuListItem(text, **kwargs)
        
        if self.selected is None and kwargs.get('selectable', False):
            self.selected = len(self.textList)
            newEntry.selected = True

        self.textList.append(newEntry)

    def decrementSelected(self):
        if self.numSelectable == 0:
            return
            
        for idx in range(self.selected-1, -1, -1):
            if not self.textList[idx].selectable:
                continue
            else:
                self.textList[self.selected].selected = False
                self.textList[idx].selected = True
                self.selected = idx
                break

    def incrementSelected(self):
        if self.numSelectable == 0:
            return

        for idx in range(self.selected+1, len(self.textList)):
            if not self.textList[idx].selectable:
                continue
            else:
                self.textList[self.selected].selected = False
                self.textList[idx].selected = True
                self.selected = idx
                break

    def redrawMenuBody(self):
        gfxTextList = []
        
        for entry in self.textList:
            if entry.selected:
                gfxEntry = [entry.text, entry.textColorSel, entry.bgColorSel]
            else:
                gfxEntry = [entry.text, entry.textColorUnsel, entry.bgColorUnsel]
            gfxTextList.append(gfxEntry)
        graphics.drawTextList(self.menuSurface, gfxTextList)

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
        elif event.key == pygame.K_UP:
            self.decrementSelected()      
        return 'continue'

class SaveLoadMenu(TextListMenu):
    def initTextList(self):
        self.textList = []
        self.addItem('Save/Load', selectable=False, 
                                  textColorUnsel=constants.COLOR_BLACK,
                                  bgColorUnsel=constants.COLOR_GREY)
        self.addItem('Save', selectable=True)
        self.addItem('Load', selectable=True)
 
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
        self.textList = []
        self.addItem('Inventory', selectable=False, 
                                  textColorUnsel=constants.COLOR_BLACK,
                                  bgColorUnsel=constants.COLOR_GREY)
        
        for obj in self.actor.container.inventory:
            if obj.deleted:
                 continue
            self.addItem(obj.name, selectable=True)

    def parseEvent(self, event):
        ret = super().parseEvent(event)
        if ret == 'continue':
            return None

        if len(self.textList) == 1: #empty inventory
            return 

        elif event.key == pygame.K_d:
            #print('dropping')
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

        self.textList = [[f, constants.COLOR_WHITE,constants.COLOR_BLACK] for f in allFiles]
 
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
    #GAME.currentLevelIdx = newGame.currentLevelIdx
    GAME.currentLevel = newGame.currentLevel
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
