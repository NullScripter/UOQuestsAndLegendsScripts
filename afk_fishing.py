__version__ = "1.2"
from AutoComplete import *


# AFK Fishing Script
# The script will move the boat between two X coordinates, back and forth east to west.
# Instructions:
# 1) The player needs to be inside their boat (I recommend using the smallest one).
# 2) The boat needs to be facing east or west (the direction it will navigate)
# 3) You can have evo insectoids in the boat (you can retrieve the entrance planks to avoid them roaming away)
#
# The player will yell the boat to move forward when fish stops bitting and to turn around
# if they get past the X coordinates set.

# Tested on: RazorEnchanced v0.8.2.242; UO Quest and Legends (April 3rd 2025) 

# Personal Settings
FISHING_POLE = 0x408577AC
EASTMOST_X = 960
WESTMOST_X = 1300

CUT_ALL_FOOTWEAR = False  # Warning! Ensure you don't have yours/valuable shoes in your bag
FOOTWEAR_SCISSORS = 0x40EED929


###################################################################
# Other settings (do not change unless you know what you are doing)
FISHING_DELAY = 8500
DELAY_BETWEEN_ITEM_COLLECTIONS = 20000
DRAG_DELAY = 700
MOVING_DELAY = 500
TURN_AROUND_TIMER = 60000 * 5 # 5min

def ManageWeight():
    if Timer.Check('Collect'): return
    if CUT_ALL_FOOTWEAR:
        Items.UseItem(FOOTWEAR_SCISSORS)
        Misc.Pause(DRAG_DELAY)
    Player.ChatSay(89, '[Collectitems')
    Misc.Pause(DRAG_DELAY)
    Timer.Create('Collect', DELAY_BETWEEN_ITEM_COLLECTIONS)
    
def FishRelative(relative_tile):
    if Player.Direction not in {'North', 'South'}:
        Player.Walk('North')

    Items.UseItem(FISHING_POLE)
    Target.WaitForTarget(5000)
    Target.TargetExecuteRelative(Player.Serial, relative_tile)
    Misc.Pause(FISHING_DELAY) 
    
def MoveBoatAhead(tiles=8):
    if (Player.Position.X < EASTMOST_X or Player.Position.X > WESTMOST_X) and not Timer.Check('TurnAround'):
        Player.ChatSay(89, 'Turn Around')
        Misc.Pause(MOVING_DELAY)
        Timer.Create('TurnAround', TURN_AROUND_TIMER)

    for i in range(tiles):
        Player.ChatSay(89, 'Forward One')
        Misc.Pause(MOVING_DELAY)

while True:
    ManageWeight()    
    Journal.Clear()
    FishRelative(relative_tile=-4) # Alternate fishign North/South capturing 2 veins
   
    if Journal.Search('biting here'): 
        MoveBoatAhead(tiles=8) # Move 1 vein ahead
    
