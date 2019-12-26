from qQuest.constants import SpriteDict 

EFFECTS = {}
EFFECTS['fow_oneSide'] = {
    'spriteDict' : (SpriteDict('16x16figs/fogOfWarPositiveB.png', 
                        colIdx=0, rowIdx=0, numSprites=1),)}
EFFECTS['fow_twoSide'] = {
    'spriteDict' : (SpriteDict('16x16figs/fogOfWarPositiveB.png', 
                        colIdx=1, rowIdx=0, numSprites=1),)}
EFFECTS['fow_threeSide'] = {
    'spriteDict' : (SpriteDict('16x16figs/fogOfWarPositiveB.png', 
                        colIdx=2, rowIdx=0, numSprites=1),)}
EFFECTS['fow_fourSide'] = {
    'spriteDict' : (SpriteDict('16x16figs/fogOfWarPositiveB.png', 
                        colIdx=3, rowIdx=0, numSprites=1),)}
EFFECTS['fow_twoSideB'] = {
    'spriteDict' : (SpriteDict('16x16figs/fogOfWarPositiveB.png', 
                        colIdx=1, rowIdx=1, numSprites=1),)}

EFFECTS['fullHeart'] = {
    'spriteDict' : (SpriteDict('dawnlike/GUI/GUI0.png', 
                        colIdx=0, rowIdx=1, numSprites=1),)}
EFFECTS['emptyHeart'] = {
    'spriteDict' : (SpriteDict('dawnlike/GUI/GUI0.png', 
                        colIdx=4, rowIdx=1, numSprites=1),)}

EFFECTS['monsterEmote'] = {
    'spriteDict' : (SpriteDict('dawnlike/GUI/GUI0.png', 
                        colIdx=11, rowIdx=3, numSprites=1),)}

EFFECTS['questionEmote'] = {
    'spriteDict' : (SpriteDict('dawnlike/GUI/GUI0.png', 
                        colIdx=13, rowIdx=3, numSprites=1),)}

EFFECTS['fireSmall'] = {
    'spriteDict' : (SpriteDict('dawnlike/Objects/Effect0.png', 
                        colIdx=0, rowIdx=21, numSprites=1),)}
