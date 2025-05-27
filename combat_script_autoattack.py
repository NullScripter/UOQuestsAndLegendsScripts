__version__ = "1.0.0"

# Combat Script to auto-attack nearby monsters in range.
# It keeps buffs active, use specials, and use bandages when needed. 
# The script will run forever (until you manually pause it) and you can set it to start on login. 
# Tested on: RazorEnchanced v0.8.2.242; UO Quest and Legends (May 24th 2025) 

# Personal Settings (change to yours!)
MAIN_WEAPON = 0x4056A181 
WEAPON_RANGE = 6
WEAPON_SPECIAL = 'Primary' # Set to 'Primary', 'Secondary' or 'None' to not use a special

ATTACK_INNOCENTS = False  # Change to True to attack blues (e.g. for Twalo and Lord Oaks)

MANA_RESERVE = 55  # Wont use specials/spells if below this value 
HITPOINTS_PERCENT_TO_HEAL = 0.7
STAMINA_PERCENT_TO_DIVINE_FURY = 0.7

ADDITIONAL_DELAY = 50 # Increase this value based on your ping until you get no 'already casting' message.
# (The ADDITIONAL_DELAY is added on top of the expected spell casting time, when relevant)

BUFF_SETTINGS = {
    # Forms
    'Vampiric Embrance': True, 
    'Wraith Form': False, 

    # Regular Buffs
    'Protection': True,
    'Consecrate Weapon': False,
    'Divine Fury': False, # Set to False if you dont need the stats (will still cast if low in stamina)
    'Curse Weapon': False, # Will only cast if at less than 50% life
    'Magic Reflection': True,

    # Dispell
    'Cleansing Wind': True, # To remove curses and other debuffs

    # Parry Mastery
    'Heighten Senses': False,
    'Shield Bash': False,
}


####################################################################
### Main Script (dont change unless you know what you are doing) ###

from AutoComplete import *
from System.Collections.Generic import List
from System import Byte

def GetNearbyEnemies(maxRange=12):
    enemy_filter = Mobiles.Filter()
    enemy_filter.Enabled = True
    enemy_filter.RangeMax = maxRange
    enemy_filter.CheckLineOfSight = True
    enemy_filter.Notorieties = List[Byte](bytes([1,3,4,5,6])) if ATTACK_INNOCENTS else List[Byte](bytes([3,4,5,6]))
    return Mobiles.ApplyFilter(enemy_filter )
     
    
def CastSpell(spellname, cast_delay=0, target_serial=None):
    Spells.Cast(spellname)
    if target_serial:
        Target.WaitForTarget(5000+ADDITIONAL_DELAY)
        Target.TargetExecute(target_serial)
    else:
        Misc.Pause(cast_delay+ADDITIONAL_DELAY)
  

def AttackRotation(enemy):
    # Note: Shield bash need to always be used before weapon special
    if BUFF_SETTINGS['Shield Bash'] and not Player.BuffsExist('Shield Bash'):
        CastSpell('Shield Bash', cast_delay=250)

    if WEAPON_SPECIAL == 'Primary' and not Player.HasPrimarySpecial:
        Player.WeaponPrimarySA() 
    
    if WEAPON_SPECIAL == 'Secondary' and not Player.HasSecondarySpecial:
        Player.WeaponSecondarySA() 
    
    Misc.Pause(250)        
    Player.Attack(enemy)


def SpellPriorityRotation():
    # Life/Poison/Stamina recovery
    if Player.Hits < HITPOINTS_PERCENT_TO_HEAL * Player.HitsMax or Player.BuffsExist('Poisoned'):
        Player.ChatSay('[bandageself')

    if Player.Mana < MANA_RESERVE:
        return Misc.Pause(250)
    
    if Player.Stam < Player.StamMax * STAMINA_PERCENT_TO_DIVINE_FURY:
        return CastSpell('Divine Fury', cast_delay=1000)
    
    # Curse Removal
    if BUFF_SETTINGS['Cleansing Wind'] and (Player.BuffsExist("Curse") or Player.BuffsExist("Clumsy") or Player.BuffsExist("Feeblemind") or Player.BuffsExist("Weaken") or Player.BuffsExist("Corpse Skin") or Player.BuffsExist("Strangle") or Player.BuffsExist("Mind Rot") or Player.BuffsExist("Blood Oath (curse)")):
        return CastSpell('Cleansing Wind', target_serial=Player.Serial)

    # Buffs
    if BUFF_SETTINGS['Protection'] and not Player.BuffsExist('Protection'):
        return CastSpell('Protection', cast_delay=750)
    
    if BUFF_SETTINGS['Divine Fury'] and not Player.BuffsExist('Divine Fury'):
        return CastSpell('Divine Fury', cast_delay=1000)
    
    if BUFF_SETTINGS['Consecrate Weapon'] and not Player.BuffsExist('Consecrate Weapon'):
        return CastSpell('Consecrate Weapon', cast_delay=500)
    
    if BUFF_SETTINGS['Curse Weapon'] and Player.Hits < Player.HitsMax*0.9 and not Player.BuffsExist('Curse Weapon'):
        return CastSpell('Curse Weapon', cast_delay=1000)
    
    if BUFF_SETTINGS['Magic Reflection'] and not Player.BuffsExist('Magic Reflection'):
        return CastSpell('Magic Reflection', cast_delay=1250)
    
    if BUFF_SETTINGS['Heighten Senses'] and not Player.BuffsExist('Heighten Senses'):
        return CastSpell('Heighten Senses', cast_delay=1000)

    # Forms
    if BUFF_SETTINGS['Vampiric Embrance'] and not Player.BuffsExist('Vampiric Embrance'):
        return CastSpell('Vampiric Embrance', cast_delay=2250)
    
    if BUFF_SETTINGS['Wraith Form'] and not Player.BuffsExist('Wraith Form'):
        return CastSpell('Wraith Form', cast_delay=2250)

def Main():
    Misc.Pause(1000) # Small delay in case of start on login
    Player.WeaponPrimarySA() # Set a special to reset any 'ghost' value in the client from disconnect and reconnect

    while Player.Connected:
        enemies = GetNearbyEnemies(WEAPON_RANGE)
        enemy = enemies[0] if len(enemies) > 0 else None
        
        while enemy and Player.DistanceTo(enemy) <= WEAPON_RANGE: # Keep atking the same enemy
            monster = Mobiles.FindBySerial(enemy.Serial) # To confirm enemy is still alive
            if monster is None: break
             
            SpellPriorityRotation()
            AttackRotation(enemy)
            Misc.Pause(250)

        SpellPriorityRotation()
        Misc.Pause(500) 

Main()
