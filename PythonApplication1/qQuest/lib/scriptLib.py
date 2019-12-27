from collections import namedtuple
from typing import Tuple, List

''' All of this lends pretty well to dictionaries/JSON.  This constriction is
(hopefully) for readbility.

'''

''' Text is the text provided with a selectable script interaction option.
Goto is the next portion of the script if this option is selected'''
Option = namedtuple('Option', ['text', 'goto'])


# class Script(dict): 
#     ''' The main class that makes up a script.  It's basically just a dictionary
#     with scriptIDs (e.g. 'start') as key, and ScriptLines as values.'''
#     def addLine(self, lineID: str, scriptLine: ScriptLine) -> None:
#         if lineID in self:
#             raise ValueError(f'LineID "{lineID}" already in script."')
#         self[name] = ScriptLine
        

# class ScriptLine():
#     def __init__(self, readText: str, userOptions: List[Option]):
#         self.readText = readText
#         self.userOptions = []
    
    # def addOption(self, option: Option) -> None:
    #     self.userOptions.append(option)

    # def addStatCheck(self):
    #     pass
    
    # def addItemCheck(self):
    #     pass

    # def addAccomplishmentCheck(self):
    #     pass

    # def addTrigger(self):
    #     pass

SCRIPTS = {}

# script = Script()
# line = ScriptLine('Would you like to go to A or B?')
SCRIPTS['baseNPCscript'] =  {
    'start' : {
        'readText' : 'Would you like to go to A or B?',
        'options' : (
            Option(text="doesn't A sound great?", goto="A"),
            Option(text="doesn't B sound great?", goto="B"))
    },
    'A' : {
        'readText' : 'Welcome to A!',
    }, 
    'B' : {
        'readText' : 'Welcome to B!',
    }              
    }
