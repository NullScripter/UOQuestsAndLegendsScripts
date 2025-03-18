__version__ = "1.0"
from AutoComplete import *

# Script to AFK while Evo Insectoid collect resouces on open areas.
# The pets may wander too far away and miss the auto-feed trigger.
# This script:
# 1) Call [CollectItems every 30s, so you are never over item limit and miss power saves.
# 2) Call [BringInsectoids and feed them every 30min (cost 5k per use) so keep them loyal


# Personal Settings
PORTABLE_PET_FEEDER = 0x4106E4EB

# Script
while True:
    Player.ChatSay(89, '[CollectItems')
    Misc.Pause(30000)
        
    if not Timer.Check('FeedTimer'):
        Timer.Create('FeedTimer', 30*60000)
        Player.ChatSay(89,'[BringInsectoids')   
        Misc.Pause(500)  
        Items.UseItem(PORTABLE_PET_FEEDER)
    
    Misc.Pause(500)  
        
