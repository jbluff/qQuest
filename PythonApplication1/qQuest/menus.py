import os
import datetime
import copy

import dill
import pygame

from qQuest import constants
from qQuest import graphics
from qQuest.graphics import SURFACE_MAIN
from qQuest.game import CLOCK, GAME 

DATETIME_FORMAT = '%Y%m%d%H%M%S'
SAVEPATH = os.path.join(os.path.dirname(__file__),"..","saves")

class MenuListItem():
    ''' Items which are elements in a Menu, both selectable and not.
    Right now that mostly means carrying colors and text around, but we will
    generalize eventually, for sliders and buttons and such.'''
    def __init__(self, text,
                       textColorUnsel=constants.COLOR_WHITE, 
                       bgColorUnsel=constants.COLOR_BLACK, 
                       selectable=True, 
                       textColorSel=constants.COLOR_RED, 
                       bgColorSel=constants.COLOR_DGREY,
                       selected=False,
                       annotation=None):
        self.text = text
        self.textColorUnsel = textColorUnsel
        self.bgColorUnsel = bgColorUnsel
        self.selectable = selectable
        self.textColorSel = textColorSel
        self.bgColorSel = bgColorSel
        self.selected = selected
        self.annotation = annotation

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

    def calculateDrawPosition(self) -> None:
        ''' Calculate where the upper left corner of the menu should be 
        drawn on the screen.'''
        windowWidth = constants.CELL_WIDTH*constants.CAMERA_WIDTH
        windowHeight = constants.CELL_HEIGHT*constants.CAMERA_HEIGHT
        self.coordY = (windowHeight-self.menuHeight)/2
        self.coordX = (windowWidth-self.menuWidth)/2

    def mainLoop(self) -> None:
        ''' Infinite loop for menu operation'''
        
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

    def redrawMenu(self) -> None:
        ''' Redraw the menu, respecting FPS limits.'''
        self.menuSurface.fill(constants.COLOR_BLACK)
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
    def __init__(self):
        super().__init__(SURFACE_MAIN, menuSize=(200,50))

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
    def __init__(self):
        self.selected=None
        self.initTextList()
        super().__init__(SURFACE_MAIN)

    def initTextList(self):
        raise NotImplemented("sinitTextList must be overwritten by children")

    def restartLoop(self):
        pass
    
    @property
    def numSelectable(self) -> int:
        ''' how many selectable objects are in the menu? '''
        return sum([entry.selectable for entry in self.menuList])

    def addMenuItem(self, text: str, **kwargs) -> None:
        ''' Add an entry to the text list menu'''
        newEntry = MenuListItem(text, **kwargs)
        
        if self.selected is None and kwargs.get('selectable', False):
            self.selected = len(self.menuList)
            newEntry.selected = True

        self.menuList.append(newEntry)

    def decrementSelected(self) -> None:
        if self.numSelectable == 0:
            return
            
        for idx in range(self.selected-1, -1, -1):
            if not self.menuList[idx].selectable:
                continue
            else:
                self.menuList[self.selected].selected = False
                self.menuList[idx].selected = True
                self.selected = idx
                break

    def incrementSelected(self) -> None:
        if self.numSelectable == 0:
            return

        for idx in range(self.selected+1, len(self.menuList)):
            if not self.menuList[idx].selectable:
                continue
            else:
                self.menuList[self.selected].selected = False
                self.menuList[idx].selected = True
                self.selected = idx
                break

    def redrawMenuBody(self) -> None:
        gfxTextList = []
        
        for entry in self.menuList:
            if entry.selected:
                gfxEntry = [entry.text, entry.textColorSel, entry.bgColorSel]
            else:
                gfxEntry = [entry.text, entry.textColorUnsel, entry.bgColorUnsel]
            gfxTextList.append(gfxEntry)
        graphics.drawTextList(self.menuSurface, gfxTextList)

    def finishLoop(self):
        pass

    def parseEvent(self, event) -> str:
        if event.type != pygame.KEYDOWN:
            return 'continue'
                    
        if event.key == pygame.K_q:
            self.breakLoop = True
            return ''

        elif event.key == pygame.K_DOWN:
            self.incrementSelected()
            return 'continue'

        elif event.key == pygame.K_UP:
            self.decrementSelected()      
            return 'continue'

        return ''


class SaveLoadMenu(TextListMenu):
    def initTextList(self):
        self.menuList = []
        self.addMenuItem('Save/Load', selectable=False, 
                                  textColorUnsel=constants.COLOR_BLACK,
                                  bgColorUnsel=constants.COLOR_GREY)
        self.addMenuItem('Save', selectable=True)
        self.addMenuItem('Load', selectable=True)
 
    def parseEvent(self, event) -> None:
        ret = super().parseEvent(event)
        if ret == 'continue':
            return None

        if event.key == pygame.K_RETURN:
            if self.selected == 1:
                gameSave()

            elif self.selected == 2:
                LoadMenu()
                self.breakLoop = True


class LoadMenu(TextListMenu):
    def initTextList(self) -> None:
        self.menuList = []
        allFiles = listSavedGames()
        [self.addMenuItem(f, selectable=True) for f in allFiles]

    def parseEvent(self, event)-> None:
        ret = super().parseEvent(event)
        if ret == 'continue':
            return None

        if event.key == pygame.K_RETURN:
            fname = self.menuList[self.selected].text
            loadGame(fname)
            self.breakLoop = True


class InventoryMenu(TextListMenu):
    def __init__(self, actor):
        self.actor = actor
        super().__init__()

    def initTextList(self) -> None:
        self.menuList = []
        self.addMenuItem('Inventory', selectable=False, 
                                  textColorUnsel=constants.COLOR_BLACK,
                                  bgColorUnsel=constants.COLOR_GREY)
        
        for obj in self.actor.container.inventory:
            if obj.deleted:
                 continue
            self.addMenuItem(obj.name, selectable=True, annotation=obj)

    def parseEvent(self, event):
        ''' event is PyGame event, unsure of typing '''
        ret = super().parseEvent(event)
        if ret == 'continue':
            return None

        if len(self.menuList) == 1: #empty inventory
            return 

        elif event.key == pygame.K_d:
            item = self.menuList[self.selected].annotation
            item.drop()
            self.removeSelectedItemFromList()

        elif event.key == pygame.K_u:
            item = self.menuList[self.selected].annotation

            success = item.use(self.actor) #this won't always be at self.actor.
            if success:
                GAME.addMessage(self.actor.name + " uses " + item.name)
                if item.deleted:
                    self.removeSelectedItemFromList()

    def removeSelectedItemFromList(self):
        selectedCopy = copy.deepcopy(self.selected)
        self.decrementSelected()
        del self.menuList[selectedCopy]
        self.redrawGame = True


def gameSave(saveName: str='default') -> None:
    ''' dump the GAME object to a dill file. '''
    dt = datetime.datetime.now()
    dtString = dt.strftime(DATETIME_FORMAT)

    fileName = dtString + '_' + saveName + '.sav'
    filePath = os.path.join(SAVEPATH,fileName)
    GAME.addMessage(f'Game saved to {fileName}')
    print(filePath)
    with open(filePath, 'wb') as f:
        dill.dump(GAME, f)
    pass


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
    GAME.camera = newGame.camera

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
