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


def inventory(parentSurface, actor):
    menuWidth = 200
    menuHeight = 300
    #Font..

    windowWidth = parentSurface.get_width()
    windowHeight = parentSurface.get_height()

    coordY = (windowHeight-menuHeight)/2
    coordX = (windowWidth-menuWidth)/2

    inventorySurface = pygame.Surface((menuWidth, menuHeight))

    #TODO:  bgColor
    invList = [["Inventory:", constants.COLOR_WHITE],]
    invList.extend([[obj.name,constants.COLOR_GREY] for obj in actor.container.inventory])
    selected = 0
    invList = updateSelected(invList, selected)

    breakMenuLoop = False
    while not breakMenuLoop:
        # Clear
        inventorySurface.fill(constants.COLOR_BLACK)

        # Register changes
        eventsList = pygame.event.get()
        for event in eventsList:
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_i or event.key == pygame.K_q:
                    breakMenuLoop = True
                    break

                if invList == 1: #empty inventory
                    continue 
                if event.key == pygame.K_DOWN:
                    if selected < len(invList) - 2:
                        selected += 1

                elif event.key == pygame.K_UP:
                    if selected > 0:
                        selected -= 1
                   
                elif event.key == pygame.K_d:
                    actor.container.inventory[selected].drop() #fix this nonsense.
                    del invList[selected+1]
                    if selected > 0:
                        selected -= 1

                elif event.key == pygame.K_u:
                    invObj = actor.container.inventory[selected] # selected item's Actor.
                    GAME.addMessage(actor.name + " uses " + invObj.name )
                    #invObj.item.useFunction(actor.creature)
                    invObj.use(actor)
                    #del invObj #delete from inventory
                    del invList[selected+1] #delete from list
                    if selected > 0:
                        selected -= 1


                invList = updateSelected(invList, selected)
                
        # Draw
        graphics.drawTextList(inventorySurface, invList)

        # Display
        parentSurface.blit(inventorySurface, (coordX, coordY))
        CLOCK.tick(constants.GAME_FPS)
        pygame.display.flip()
        