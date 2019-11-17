import pygame

from qQuest import constants
from qQuest import graphics
from qQuest.qqGlobal import CLOCK, SURFACE_MAIN, GAME


class Menu:
    def __init__(self, parentSurface, menuSize=(300,200)):
        self.parentSurface = parentSurface
        self.menuWidth, self.menuHeight = menuSize

        windowWidth = constants.CELL_WIDTH*constants.MAP_WIDTH
        windowHeight = constants.CELL_HEIGHT*constants.MAP_HEIGHT

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
                graphics.drawGame()
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

        
class InventoryMenu(Menu):
    def __init__(self, parentSurface, actor):
        self.actor = actor
        self.selected = 0
        super().__init__(parentSurface)

    def restartLoop(self):
        self.invList = [["Inventory:", constants.COLOR_WHITE],]
        self.invList.extend([[obj.name,constants.COLOR_GREY] for obj in self.actor.container.inventory if not obj.deleted])
        self.updateSelected() #this really only needs to be called in the init

        self.menuSurface.fill(constants.COLOR_BLACK) # this shouldn't really be here.

    def finishLoop(self):
        #self.updateSelected()
        pass

    def parseEvent(self, event):

        if event.type != pygame.KEYDOWN:
            return
                    
        if event.key == pygame.K_i or event.key == pygame.K_q:
            self.breakLoop = True
            return

        if len(self.invList) == 1: #empty inventory
            return 

        if event.key == pygame.K_DOWN:
            self.incrementSelected()

        elif event.key == pygame.K_UP:
            self.decrementSelected()
            
        elif event.key == pygame.K_d:
            self.actor.container.inventory[self.selected].drop() #fix this nonsense.
            del self.invList[self.selected+1]
            self.decrementSelected()
            self.redrawGame = True

        elif event.key == pygame.K_u:
            invObj = self.actor.container.inventory[self.selected] # selected item's Actor.
            
            success = invObj.use(self.actor)

            if success:
                GAME.addMessage(self.actor.name + " uses " + invObj.name )
                if invObj.deleted:
                    del self.invList[self.selected+1] #delete from menu list -- doesn't really work.
                    self.decrementSelected()
            self.redrawGame = True

    def redrawMenuBody(self):
        graphics.drawTextList(self.menuSurface, self.invList)

    def updateSelected(self):
        numItems = len(self.invList)-1
        for idx in range(1,numItems+1):
            if idx == self.selected+1:
                self.invList[idx][1] = constants.COLOR_RED
            else:
                self.invList[idx][1] = constants.COLOR_GREY

    def decrementSelected(self):
        if self.selected > 0:
            self.selected -= 1
        self.updateSelected()

    def incrementSelected(self):
        if self.selected < len(self.invList) - 2:
            self.selected += 1
        self.updateSelected()
