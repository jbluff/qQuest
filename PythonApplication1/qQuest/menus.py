import os
import datetime
import copy
from typing import List

import dill
import pygame

from qQuest import constants, graphics
from qQuest.constants import CLOCK 


DATETIME_FORMAT = '%Y%m%d%H%M%S'
SAVEPATH = os.path.join(os.path.dirname(__file__),"..","saves")
DEFAULT_SURFACE = None

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
                #this was for showing when an item was dropped.
                #currently non-functional
                #graphics.drawGame()#fovMap=GAME.viewer.fovMap)
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


class PauseMenu(Menu):
    ''' This is a pointless thing at present, except as an example of a 
    theortically non-textList menu. '''
    def __init__(self, *args):
        super().__init__(*args, menuSize=(200,50))

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
    def __init__(self, *args, **kwargs):
        self.selected=None
        self.initTextList()
        super().__init__(*args, **kwargs)

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

    def redrawMenuBody(self, surface=None) -> None:
        if surface is None:
            surface = self.menuSurface
        gfxTextList = []
        
        for entry in self.menuList:
            if entry.selected:
                gfxEntry = [entry.text, entry.textColorSel, entry.bgColorSel]
            else:
                gfxEntry = [entry.text, entry.textColorUnsel, entry.bgColorUnsel]
            gfxTextList.append(gfxEntry)
        graphics.drawTextList(surface, gfxTextList)

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
    def __init__(self, surface, game):
        self.game = game
        self.doNext = None #this construction is bad.
        super().__init__(surface, menuSize=(200,50))

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
            self.breakLoop = True
            if self.selected == 1:
                gameSave(self.game)
            elif self.selected == 2:
                self.menuSurface.fill(constants.COLOR_BLACK)
                LoadMenu(self.parentSurface, self.game)
            
class LoadMenu(TextListMenu):
    def __init__(self, surface, game):
        self.game = game
        super().__init__(surface)

    def initTextList(self) -> None:
        self.menuList = []
        allFiles = listSavedGames()
        print(allFiles)
        [self.addMenuItem(f, selectable=True) for f in allFiles]

    def parseEvent(self, event)-> None:
        ret = super().parseEvent(event)
        if ret == 'continue':
            return None

        if event.key == pygame.K_RETURN:
            fname = self.menuList[self.selected].text
            loadGame(fname, self.game)
            self.breakLoop = True


class InventoryMenu(TextListMenu):
    def __init__(self, surface, actor):
        self.actor = actor
        super().__init__(surface)

    def initTextList(self) -> None:
        self.menuList = []
        self.addMenuItem('Inventory', selectable=False, 
                                  textColorUnsel=constants.COLOR_BLACK,
                                  bgColorUnsel=constants.COLOR_GREY)
        
        for obj in self.actor.container.inventory:
            if obj.deleted:
                 continue
            self.addMenuItem(obj.name, selectable=True, annotation=obj)

    def parseEvent(self, event) -> None:
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
                #GAME.addMessage(self.actor.name + " uses " + item.name)
                if item.deleted:
                    self.removeSelectedItemFromList()

    def removeSelectedItemFromList(self) -> None:
        selectedCopy = copy.deepcopy(self.selected)
        self.decrementSelected()
        del self.menuList[selectedCopy]
        self.redrawGame = True


def gameSave(game, saveName: str='default') -> None:
    ''' dump the GAME object to a dill file. '''
    dt = datetime.datetime.now()
    dtString = dt.strftime(DATETIME_FORMAT)

    fileName = dtString + '_' + saveName + '.sav'
    filePath = os.path.join(SAVEPATH,fileName)
    game.addMessage(f'Game saved to {fileName}')
    with open(filePath, 'wb') as f:
        dill.dump(game, f)
    pass

def loadGame(fname: str, game) -> None:

    filePath = os.path.join(SAVEPATH,fname)
    with open(filePath, 'rb') as f:
        newGame = dill.load(f)
    
    game.levels = newGame.levels
    game.currentLevel = newGame.currentLevel
    game.player = newGame.player
    game.messageHistory = newGame.messageHistory
    game.viewer = newGame.viewer
    game.camera = newGame.camera

def listSavedGames() -> List[str]:
    saveFiles = []
    for f in os.listdir(SAVEPATH):
        name = os.path.join(SAVEPATH, f)
        if not os.path.isfile(name):
            continue
        if name.endswith(".sav"):
            saveFiles.append(f)
    return saveFiles

class NpcInteractionMenu(TextListMenu):
    def __init__(self, subScript, speaker):
        ''' subScript provides (optionally) header text to read, and
        (optionally) options to follow.  This menu defines a .break attribute,
        which is the result of the menu interaction, and tells where to go to
        next in the npcs script.  A return value of 'break' ends the interaction.

        Speaker type is any Actor instance.

        this class is kind of a mess.  it doesn't have to be this bad.
        '''
        self.headerText = subScript.get('readText', None)
        self.optionList = subScript.get('options', [])
        self.result = 'break'

        self.iconSize = 64
        iconSquare = (self.iconSize, self.iconSize)
        self.iconSurface = pygame.Surface(iconSquare)
        speakerSprite = speaker.getCurrentSprite()
        pygame.transform.scale(speakerSprite, iconSquare, self.iconSurface)
        
        super().__init__(DEFAULT_SURFACE, menuSize = (self.iconSize+200, 100))
        #
        
        #self.coordX, self.coordY

    def redrawMenuBody(self, surface=None) -> None:
        if surface is None:
            surface = self.menuSurface

        gfxTextList = []
        
        for entry in self.menuList:
            if entry.selected:
                gfxEntry = [entry.text, entry.textColorSel, entry.bgColorSel]
            else:
                gfxEntry = [entry.text, entry.textColorUnsel, entry.bgColorUnsel]
            gfxTextList.append(gfxEntry)
        graphics.drawTextList(surface, gfxTextList, startX=self.iconSize)

        surface.blit(self.iconSurface, (0,0))

    def initTextList(self) -> None:
        self.menuList = []
        if self.headerText is not None:
            self.addMenuItem(self.headerText, selectable=False, 
                                    textColorUnsel=constants.COLOR_BLACK,
                                    bgColorUnsel=constants.COLOR_GREY)
        for option in self.optionList:
            self.addMenuItem(option.text, selectable=True, annotation=option.goto)
 

    def parseEvent(self, event) -> None:
        ''' event is PyGame event, unsure of typing.'''
        ret = super().parseEvent(event)
        if ret == 'continue':
            return None

        if event.key == pygame.K_RETURN:
            self.breakLoop = True

            if self.optionList != []:
                self.result = self.menuList[self.selected].annotation
            else:
                self.result = 'break'

    def finishLoop(self):
        self.redrawGame = True


class HelpMenu(TextListMenu):
    def __init__(self, surface):
        super().__init__(surface, menuSize=(200,100))

    def initTextList(self):
        self.menuList = []
        self.addMenuItem('Help!', selectable=False, 
                                  textColorUnsel=constants.COLOR_BLACK,
                                  bgColorUnsel=constants.COLOR_GREY)
        self.addMenuItem('q   Quits the game or menu', selectable=False, 
                                  textColorUnsel=constants.COLOR_WHITE,
                                  bgColorUnsel=constants.COLOR_BLACK)
        self.addMenuItem('i   Inventory menu', selectable=False, 
                                  textColorUnsel=constants.COLOR_WHITE,
                                  bgColorUnsel=constants.COLOR_BLACK)
        self.addMenuItem('s   Save/Load', selectable=False, 
                                  textColorUnsel=constants.COLOR_WHITE,
                                  bgColorUnsel=constants.COLOR_BLACK)
        self.addMenuItem('g   Pick up item', selectable=False, 
                                  textColorUnsel=constants.COLOR_WHITE,
                                  bgColorUnsel=constants.COLOR_BLACK)
        self.addMenuItem('u   Use item', selectable=False, 
                                  textColorUnsel=constants.COLOR_WHITE,
                                  bgColorUnsel=constants.COLOR_BLACK)
        self.addMenuItem('d   Drop item', selectable=False, 
                                  textColorUnsel=constants.COLOR_WHITE,
                                  bgColorUnsel=constants.COLOR_BLACK)
        self.addMenuItem('y   Go through portal', selectable=False, 
                                  textColorUnsel=constants.COLOR_WHITE,
                                  bgColorUnsel=constants.COLOR_BLACK)


