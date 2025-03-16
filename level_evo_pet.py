__version__ = "3.0"
from AutoComplete import *
import re

# Script to cast spells on the pet to level it.
# Optional 1) Can apply 'half level deed' when the pet reaches lvl 2000 
# Optional 2) Can use 'reset power hour deed' and start power hour
# (The script checks for pet lvl and if you have pewer active to avoid wasting
# deeds. The deeds need to be anywhere in your backpack, including inner bags)

# Personal Settings
PET_SERIAL = 0x000661DC 

SPELL_TO_CAST = 'Harm'

USE_ELEMENTAL_SPELLS = False # If set to true, the two spells below is used instead of the spell above
ELEMENTAL_SPELL_ON_PET = '[ces 30'  
ELEMENTAL_SPELL_FOR_MANA = '[ces 26' 

ENABLE_HALF_LEVEL_LOGIC = False 
ENABLE_POWER_HOUR_LOGIC = False 



###################################################################
# Other settings (do not change unless you know what you are doing)
HALF_LEVEL_CHECK_INTERVAL = 30000 
POWER_HOUR_CHECK_INTERVAL = 60000

## Script
def GetPetLevelFromGump():
    Gumps.CloseGump(0xb67943db)
    Misc.Pause(500)
    Misc.WaitForContext(PET_SERIAL, 2000)
    Misc.ContextReply(PET_SERIAL, 'Properties')
    Gumps.WaitForGump(0xb67943db, 5000)
    if not Gumps.HasGump(0xb67943db):
        Misc.SendMessage('ERROR: Pet Gump not found!')
        return None
    lines = Gumps.GetLineList(0xb67943db)
    for line in lines:
        if 'Current Level' in line: return line
    return None

def AutoLevelPet():
    if not ENABLE_HALF_LEVEL_LOGIC or Timer.Check('CheckHalfLevel'): return
    Timer.Create('CheckHalfLevel', HALF_LEVEL_CHECK_INTERVAL)

    pet = Mobiles.FindBySerial(PET_SERIAL)
    if pet is None: 
        Misc.Beep() 
        return Misc.SendMessage('ERROR: Pet not found!', 0x21)

    pet_level = GetPetLevelFromGump()
    if pet_level is None:
        return Misc.SendMessage('ERROR: Level not found!', 0x21)    

    Misc.SendMessage(f'{pet.Name} - {pet_level}', 0x21) 
    if pet_level != 'Current Level: 2000':
        return Misc.SendMessage('Not yet time to half level', 0x21) 
    
    deed = Items.FindByName('Evo Half Level Deed', -1, Player.Backpack.Serial, 5)
    if deed is None: 
        Misc.Beep() 
        return Misc.SendMessage('ERROR: Evo Half Level Deed not found!', 0x21)
    
    Items.UseItem(deed)
    Target.WaitForTarget(2000)
    if Target.HasTarget(): Target.TargetExecute(pet) 


def StartPowerHour():
    if not ENABLE_POWER_HOUR_LOGIC or Timer.Check('CheckPowerHour'): return
    Timer.Create('CheckPowerHour', POWER_HOUR_CHECK_INTERVAL)

    Journal.Clear()
    Player.ChatSay(0x21,'[PowerHour')
    Misc.Pause(1000)
    
    line = Journal.GetLineText('You cannot use Power Hour yet')
    if line is None: 
        return Misc.SendMessage('Power Hour Started!', 0x21)

    match = re.search(r'\d+(\.\d+)?', line)
    if match is None:
        return Misc.SendMessage('ERROR: Failure checking power hour cooldown!', 0x21)
    cooldown_hours = float(match.group()) / 60
    
    if cooldown_hours > 23:
        return Misc.SendMessage(f'Power hour should be active! (Coolddown: {cooldown_hours:.1f}h)', 0x21)
    
    Misc.SendMessage(f'Restarting Power Hour! (Coolddown: {cooldown_hours:.1f}h)', 0x21)
        
    deed = Items.FindByName('Reset Power Hour Deed', -1, Player.Backpack.Serial, 5)
    if deed is None: 
        Misc.Beep() 
        return Misc.SendMessage('ERROR: Reset Power Hour Deed not found!', 0x21)
    
    Items.UseItem(deed)
    Misc.Pause(500)
    Player.ChatSay(0x21,'[PowerHour')


while True:
    AutoLevelPet()
    StartPowerHour()

    if USE_ELEMENTAL_SPELLS:
        Player.ChatSay(0x21, ELEMENTAL_SPELL_ON_PET)
        Target.WaitForTarget(5000)
        if Target.HasTarget(): Target.TargetExecute(PET_SERIAL)

        if ELEMENTAL_SPELL_FOR_MANA and Player.Mana * 0.5:
            Player.ChatSay(0x21, ELEMENTAL_SPELL_FOR_MANA)
            Misc.Pause(1500)
    else:
        Spells.Cast(SPELL_TO_CAST)
        Target.WaitForTarget(5000)
        if Target.HasTarget(): Target.TargetExecute(PET_SERIAL)
