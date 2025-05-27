__version__ = "1.0.2"

# Combat Script for spell casting rotation (not begginer friendly)
# WARNING: You will need to incorporate your own mana recovery of choice to the script 
# on your own, otherwise just use Wraith Form (way too many mana regen options to generalize).
# Check line 104 if you want to add your buff/logic for it.

# 1) The script will keep buffs active (check BUFF_SETTINGS at line 25 to turn them on/off)
# 2) The script will use the combat spell if an enemy is nearby (check SPELL_ROTATION at line 46). 
# 3) The script will run forever (until you manually pause it) and you can set it to start on login.
# Tested on: RazorEnchanced v0.8.2.242; UO Quest and Legends (May 24th 2025) 

# Personal Settings (change to yours!)
ENEMY_LOOKUP_RANGE = 10 
ATTACK_INNOCENTS = False  # Change to True to attack blues (e.g. for Twalo and Lord Oaks)

MANA_RESERVE = 55  # Wont use specials/spells if below this value 
HITPOINTS_PERCENT_TO_HEAL = 0.8
STAMINA_PERCENT_TO_DIVINE_FURY = 0.2

ADDITIONAL_DELAY = 100 # Increase/reduce this value based on your ping. 
# If you are getting 'already casting' messages, it means you need to increase this value.
# (The ADDITIONAL_DELAY is added on top of the expected spell casting time when relevant)

BUFF_SETTINGS = { 
    # Forms
    'Vampiric Embrance': False, 
    'Wraith Form': False, 

    # Regular Buffs
    'Protection': True,
    'Magic Reflection': True,
    'Arcane Empowerement': False,

    # Dispell
    'Cleansing Wind': True, # To remove curses and other debuffs

    # Parry Mastery
    'Heighten Senses': False,
}

class SpellSetting():
    def __init__(self, spell_id, cast_delay=0, target_self=False, target_enemy=False):
        self.spell_id, self.cast_delay, self.target_self, self.target_enemy = spell_id, cast_delay, target_self, target_enemy

SPELL_ROTATION = [ 
    # Example 1) Mage Rotation
    SpellSetting('Fireball', target_enemy=True), # Fireball will wait for targeting and target the enemy 
    SpellSetting('Wither', cast_delay=500), # Wither has no target - will wait its 0.5 casting time

    # Example 2) Spellweaver Rotation
    SpellSetting('Thunderstorm', cast_delay=500), # Thunderstorm has no target - will wait its 0.5 casting time
    SpellSetting('Wildfire', cast_delay=2500),  # Wildfire has no target now - will wait the 2.5s casting time

    # Example 3) Tome of Spell Making 
    # SpellSetting(0x4045701C, cast_delay=1100), # "Self" mode (1.1s cast delay / no targeting expected)  
    # SpellSetting(0x4044E1DA, target_enemy=True), # "Choose" mode (targeting enemy)
    # SpellSetting(0x401742A0, target_self=True), # "Choose" mode (targeting self)

    # Example 4) Elemental Spell Rotation
    SpellSetting('[cfs 8', target_self=True), # Mass Lower Fire
    SpellSetting('[cfs 10', target_self=True), # Mass Fire Arrow
] 



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
     
    
def CastSpell(spell_id, cast_delay=0, target_serial=None):
    if isinstance(spell_id, int): # Item Serial (spell making or elemetal spell)
        Items.UseItem(spell_id)
    elif spell_id[0] == '[': # Command (elemental spell)
        Player.ChatSay(spell_id)
    else: # Tradional spell casting
        Spells.Cast(spell_id)

    if target_serial:
        Target.WaitForTarget(6000+ADDITIONAL_DELAY)
        Target.TargetExecute(target_serial)
    else:
        Misc.Pause(cast_delay+ADDITIONAL_DELAY)


def BuffRotation():
    # Life/Poison/Stamina recovery
    if Player.Hits < HITPOINTS_PERCENT_TO_HEAL * Player.HitsMax or Player.BuffsExist('Poisoned'):
        Player.ChatSay('[bandageself')

    if Player.Mana < MANA_RESERVE:
        # TIP: Consider adding your mana recovery option around here
        return Misc.Pause(250)
    
    if Player.Stam < Player.StamMax * STAMINA_PERCENT_TO_DIVINE_FURY:
        CastSpell('Divine Fury', cast_delay=1000)
    
    # Curse Removal
    if BUFF_SETTINGS['Cleansing Wind'] and (Player.BuffsExist("Curse") or Player.BuffsExist("Clumsy") or Player.BuffsExist("Feeblemind") or Player.BuffsExist("Weaken") or Player.BuffsExist("Corpse Skin") or Player.BuffsExist("Strangle") or Player.BuffsExist("Mind Rot") or Player.BuffsExist("Blood Oath (curse)")):
        CastSpell('Cleansing Wind', target_serial=Player.Serial)

    # Buffs
    if BUFF_SETTINGS['Protection'] and not Player.BuffsExist('Protection'):
        return CastSpell('Protection', cast_delay=750)
    
    if BUFF_SETTINGS['Magic Reflection'] and not Player.BuffsExist('Magic Reflection'):
        CastSpell('Magic Reflection', cast_delay=1250)
    
    if BUFF_SETTINGS['Heighten Senses'] and not Player.BuffsExist('Heighten Senses'):
        CastSpell('Heighten Senses', cast_delay=1000)

    if BUFF_SETTINGS['Arcane Empowerement'] and not Player.BuffsExist('Arcane Empowerement'):
        CastSpell('Arcane Empowerement', cast_delay=3000)
    
    # Forms
    if BUFF_SETTINGS['Vampiric Embrance'] and not Player.BuffsExist('Vampiric Embrance'):
        CastSpell('Vampiric Embrance', cast_delay=2250)
    
    if BUFF_SETTINGS['Wraith Form'] and not Player.BuffsExist('Wraith Form'):
        CastSpell('Wraith Form', cast_delay=2250)


def Main():
    Misc.Pause(1000) # Small delay in case of start on login
    
    spell_idex = 0
    while Player.Connected:
        enemies = GetNearbyEnemies(ENEMY_LOOKUP_RANGE)
        enemy = enemies[0] if len(enemies) > 0 else None
        
        BuffRotation() # Check buffs before anything

        if not enemy or Player.IsGhost: # Pause if no enemy nearby or dead
            Misc.Pause(500)
            continue

        # Cast the next spell in the rotation
        spell = SPELL_ROTATION[spell_idex]
        spell_idex = (spell_idex + 1) % len(SPELL_ROTATION) # Rotate to next index
        
        if spell.target_self:
            CastSpell(spell.spell_id, target_serial=Player.Serial)
        elif spell.target_enemy:
            CastSpell(spell.spell_id, target_serial=enemy.Serial)
        else:
            CastSpell(spell.spell_id, cast_delay=spell.cast_delay)
        # No pause after CastSpell (as the correct pause was done based on the spell used)

Main()
