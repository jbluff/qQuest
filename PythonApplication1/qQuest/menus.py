import pygame

from qQuest import constants
from qQuest import graphics
from qQuest.qqGlobal import CLOCK, SURFACE_MAIN, GAME

def updateSelected(invList, selectedIdx):
    #TODO:  bgColor
    numItems = len(invList)-1
    for idx in range(1,numItems+1):
        if idx == selectedIdx+1:
            invList[idx][1] = constants.COLOR_RED
        else:
            invList[idx][1] = constants.COLOR_GREY
    return invList

class Menu:
    def __init__(self, parentSurface, menuSize=(300,200)):
        self.parentSurface = parentSurface
        self.menuWidth, self.menuHeight = menuSize

        windowWidth = constants.CELL_WIDTH*constants.MAP_WIDTH
        windowHeight = constants.CELL_HEIGHT*constants.MAP_HEIGHT

        #textWidth, textHeight = graphics.helperTextDims(text="menuText") 

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


class InventoryMenu(Menu):
    def __init__(self, parentSurface, actor):
        self.actor = actor
        self.selected = 0
        super().__init__(parentSurface)

    def restartLoop(self):
        self.invList = [["Inventory:", constants.COLOR_WHITE],]
        self.invList.extend([[obj.name,constants.COLOR_GREY] for obj in self.actor.container.inventory if not obj.deleted])
        self.invList = updateSelected(self.invList, self.selected)

        self.menuSurface.fill(constants.COLOR_BLACK)

    def finishLoop(self):
        pass
        #self.invList = updateSelected(self.invList, self.selected)

    def parseEvent(self, event):

        if event.type != pygame.KEYDOWN:
            return
                    
        if event.key == pygame.K_i or event.key == pygame.K_q:
            self.breakLoop = True
            return

        if len(self.invList) == 1: #empty inventory
            return 

        if event.key == pygame.K_DOWN:
            if self.selected < len(self.invList) - 2:
                self.selected += 1

        elif event.key == pygame.K_UP:
            if self.selected > 0:
                self.selected -= 1
            
        elif event.key == pygame.K_d:
            self.actor.container.inventory[self.selected].drop() #fix this nonsense.
            del self.invList[self.selected+1]
            if self.selected > 0:
                self.selected -= 1
            self.redrawGame = True

        elif event.key == pygame.K_u:
            invObj = self.actor.container.inventory[self.selected] # selected item's Actor.
            
            success = invObj.use(self.actor)

            if success:
                GAME.addMessage(self.actor.name + " uses " + invObj.name )
                if invObj.deleted:
                    del self.invList[self.selected+1] #delete from menu list -- doesn't really work.
                    if self.selected > 0:
                        self.selected -= 1
            self.redrawGame = True

    def redrawMenuBody(self):
        graphics.drawTextList(self.menuSurface, self.invList)
        


### MENU FUNCTIONS ###
def pause(surface, game):
    ''' dummy function, sort of dumb '''
    game.addMessage("paused!")

    menuText = "paused"
    #TODO:  font flexibility
    windowWidth = constants.CELL_WIDTH*constants.MAP_WIDTH
    windowHeight = constants.CELL_HEIGHT*constants.MAP_HEIGHT

    textWidth, textHeight = graphics.helperTextDims(text="menuText") # font=

    coordY = (windowHeight-textHeight)/2
    coordX = (windowWidth-textWidth)/2

    breakMenuLoop = False
    while not breakMenuLoop:
        eventsList = pygame.event.get()
        for event in eventsList:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    breakMenuLoop = 1

        graphics.drawText(surface, menuText, (coordX, coordY), constants.COLOR_WHITE, bgColor=constants.COLOR_BLACK)
        CLOCK.tick(constants.GAME_FPS)
        pygame.display.flip()