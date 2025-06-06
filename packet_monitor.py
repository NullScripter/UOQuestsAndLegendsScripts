__version__ = "1.2"

from AutoComplete import *
import re

# The script will log all packets between client and server for a given amount of 
# time. At the end of this timer, a report gump is drawn with the number of packets,
# total bytes, and bytes per second, as well as the top 25 packets based on the 
# total bytes size exchanged.

# Tested on: RazorEnchanced v0.8.2.242; UO Quest and Legends (May 24th 2025) 
# Can be set to start on login (will pause after the TIMER / 5s default)

LOG_FOLDER = r'D:\Games\UO Tools\TazUO.Launcher\TazUO\Data\Plugins\RazorEnhanced-0.8.2.115\Scripts\log'
LOG_FILE = LOG_FOLDER + 'packets.log'
TIMER = 5000 # in miliseconds


# Packet list from https://docs.polserver.com/packets/index.php
UO_PACKETS_NAMES = {
    "0x0C": "Edit Tile Data (God Client)",
    "0x15": "Follow",
    "0x22": "Character Move ACK/ Resync Request",
    "0x2C": "Resurrection Menu",
    "0x39": "Remove (Group)",
    "0x3A": "Send Skills",
    "0x56": "Map Packet (cartography/treasure)",
    "0x66": "Books (Pages)",
    "0x6C": "Target Cursor Commands",
    "0x6F": "Secure Trading",
    "0x71": "Bulletin Board Messages",
    "0x72": "Request War Mode",
    "0x73": "Ping Message",
    "0x93": "Book Header ( Old )",
    "0x95": "Dye Window",
    "0x98": "All Names (3D Client Only)",
    "0x99": "Give Boat/House Placement View",
    "0x9A": "Console Entry Prompt",
    "0xB8": "Request/Char Profile",
    "0xBB": "Ultima Messenger",
    "0xBD": "Client Version",
    "0xBE": "Assist Version",
    "0xBF": "General Information Packet",
    "0xC2": "Unicode TextEntry",
    "0xC8": "Client View Range",
    "0xC9": "Get Area Server Ping (God Client)",
    "0xCA": "Get User Server Ping (God Client)",
    "0xD0": "Configuration File",
    "0xD1": "Logout Status",
    "0xD4": "Book Header ( New )",
    "0xD6": "Mega Cliloc",
    "0xD7": "Generic AOS Commands",
    "0xF1": "Freeshard List",
    "0x00": "Create Character",
    "0x01": "Disconnect Notification",
    "0x02": "Move Request",
    "0x03": "Talk Request",
    "0x04": "Request God Mode (God Client)",
    "0x05": "Request Attack",
    "0x06": "Double Click",
    "0x07": "Pick Up Item",
    "0x08": "Drop Item",
    "0x09": "Single Click",
    "0x0A": "Edit (God Client)",
    "0x12": "Request Skill etc use",
    "0x13": "Drop->Wear Item",
    "0x14": "Send Elevation (God Client)",
    "0x1E": "Control Animation",
    "0x34": "Get Player Status",
    "0x35": "Add Resource (God Client)",
    "0x37": "Move Item (God Client)",
    "0x38": "Pathfinding in Client",
    "0x3B": "Buy Item(s)",
    "0x45": "Version OK",
    "0x46": "New Artwork",
    "0x47": "New Terrain",
    "0x48": "New Animation",
    "0x49": "New Hues",
    "0x4A": "Delete Art",
    "0x4B": "Check Client Version",
    "0x4C": "Script Names",
    "0x4D": "Edit Script File",
    "0x50": "Board Header",
    "0x51": "Board Message",
    "0x52": "Board Post Message",
    "0x57": "Update Regions",
    "0x58": "Add Region",
    "0x59": "New Context FX",
    "0x5A": "Update Context FX",
    "0x5C": "Restart Version",
    "0x5D": "Login Character",
    "0x5E": "Server Listing",
    "0x5F": "Server List Add Entry",
    "0x60": "Server List Remove Entry",
    "0x61": "Remove Static Object",
    "0x62": "Move Static Object",
    "0x63": "Load Area",
    "0x64": "Load Area Request",
    "0x69": "Change Text/Emote Colors",
    "0x75": "Rename Character",
    "0x7D": "Response To Dialog Box",
    "0x80": "Login Request",
    "0x83": "Delete Character",
    "0x8D": "Character Creation ( KR + SA 3D clients only )",
    "0x91": "Game Server Login",
    "0x9B": "Request Help",
    "0x9F": "Sell List Reply",
    "0xA0": "Select Server",
    "0xA4": "Client Spy",
    "0xA7": "Request Tip/Notice Window",
    "0xAC": "Gump Text Entry Dialog Reply",
    "0xAD": "Unicode/Ascii speech request",
    "0xB1": "Gump Menu Selection",
    "0xB3": "Chat Text",
    "0xB5": "Open Chat Window",
    "0xB6": "Send Help/Tip Request",
    "0xC5": "Invalid Map (Request?)",
    "0xD9": "Spy On Client",
    "0xE0": "Bug Report (KR)",
    "0xE1": "Client Type (KR/SA)",
    "0xEC": "Equip Macro (KR)",
    "0xED": "Unequip Item Macro (KR)",
    "0xEF": "KR/2D Client Login/Seed",
    "0xF8": "Character Creation ( 7.0.16.0 )",
    "0xFA": "Open UO Store",
    "0xFB": "Update View Public House Contents",
    "0x0B": "Damage",
    "0x11": "Status Bar Info",
    "0x16": "New Health bar status update (SA)",
    "0x17": "Health bar status update (KR)",
    "0x1A": "Object Info",
    "0x1B": "Char Locale and Body",
    "0x1C": "Send Speech",
    "0x1D": "Delete Object",
    "0x1F": "Explosion",
    "0x20": "Draw Game Player",
    "0x21": "Char Move Rejection",
    "0x23": "Dragging Of Item",
    "0x24": "Draw Container",
    "0x25": "Add Item To Container",
    "0x26": "Kick Player",
    "0x27": "Reject Move Item Request",
    "0x28": "Drop Item Failed/Clear Square (God Client?)",
    "0x29": "Drop Item Approved",
    "0x2A": "Blood",
    "0x2B": "God Mode (God Client)",
    "0x2D": "Mob Attributes",
    "0x2E": "Worn Item",
    "0x2F": "Fight Occuring",
    "0x30": "Attack Ok",
    "0x31": "Attack Ended",
    "0x32": "Unknown",
    "0x33": "Pause Client",
    "0x36": "Resource Tile Data (God Client)",
    "0x3C": "Add multiple Items In Container",
    "0x3E": "Versions (God Client)",
    "0x3F": "Update Statics (God Client)",
    "0x4E": "Personal Light Level",
    "0x4F": "Overall Light Level",
    "0x53": "Reject Character Logon",
    "0x54": "Play Sound Effect",
    "0x55": "Login Complete",
    "0x5B": "Time",
    "0x65": "Set Weather",
    "0x6D": "Play Midi Music",
    "0x6E": "Character Animation",
    "0x70": "Graphical Effect",
    "0x74": "Open Buy Window",
    "0x76": "New Subserver",
    "0x77": "Update Player",
    "0x78": "Draw Object",
    "0x7C": "Open Dialog Box",
    "0x82": "Login Denied",
    "0x86": "Resend Characters After Delete",
    "0x88": "Open Paperdoll",
    "0x89": "Corpse Clothing",
    "0x8C": "Connect To Game Server",
    "0x90": "Map Message",
    "0x97": "Move Player",
    "0x9C": "Request Assistance",
    "0x9E": "Sell List",
    "0xA1": "Update Current Health",
    "0xA2": "Update Current Mana",
    "0xA3": "Update Current Stamina",
    "0xA5": "Open Web Browser",
    "0xA6": "Tip/Notice Window",
    "0xA8": "Game Server List",
    "0xA9": "Characters / Starting Locations",
    "0xAA": "Allow/Refuse Attack",
    "0xAB": "Gump Text Entry Dialog",
    "0xAE": "Unicode Speech message",
    "0xAF": "Display Death Action",
    "0xB0": "Send Gump Menu Dialog",
    "0xB2": "Chat Message",
    "0xB7": "Help/Tip Data",
    "0xB9": "Enable locked client features",
    "0xBA": "Quest Arrow",
    "0xBC": "Seasonal Information",
    "0xC0": "Graphical Effect",
    "0xC1": "Cliloc Message",
    "0xC4": "Semivisible (Smurf it!)",
    "0xC6": "Invalid Map Enable",
    "0xC7": "3D Particle Effect",
    "0xCB": "Global Que Count",
    "0xCC": "Cliloc Message Affix",
    "0xD2": "Extended 0x20",
    "0xD3": "Extended 0x78",
    "0xD8": "Send Custom House",
    "0xDB": "Character Transfer Log",
    "0xDC": "SE Introduced Revision",
    "0xDD": "Compressed Gump",
    "0xDE": "Update Mobile Status",
    "0xDF": "Buff/Debuff System",
    "0xE2": "New Character Animation (KR)",
    "0xE3": "KR Encryption Response",
    "0xF0": "Krrios client special",
    "0xF3": "Object Information (SA)",
    "0xF5": "New Map Message"
}


def LogPackets():
    PacketLogger.Reset()
    PacketLogger.DiscardAll(True)
    PacketLogger.DiscardShowHeader(True)
    PacketLogger.Start(LOG_FILE)
    Misc.Pause(TIMER)
    PacketLogger.Stop()

def ParseLoggedPackets():
    client_to_server, server_to_client = dict(), dict()
    pattern = r'(\d{2}:\d{2}:\d{2}\.\d{4}): (Client -> Server|Server -> Client) \[BLOCKED\] (0x[0-9A-Fa-f]+) \(Length: (\d+)\)'
    with open(LOG_FILE, 'r') as file:
        for line in file:
            match = re.match(pattern, line)
            if match:
                timestamp, direction, packet_id, size = match.groups()
                size = int(size)
                if direction == "Client -> Server":
                    if packet_id not in client_to_server:
                         client_to_server[packet_id] = {'packet_id': packet_id, 'count': 0, 'size': 0}
                    client_to_server[packet_id]['count'] += 1
                    client_to_server[packet_id]['size'] += size
                elif direction == "Server -> Client":
                    if packet_id not in server_to_client:
                         server_to_client[packet_id] = {'packet_id': packet_id, 'count': 0, 'size': 0}
                    server_to_client[packet_id]['count'] += 1
                    server_to_client[packet_id]['size'] += size
    return client_to_server, server_to_client


def DrawGumpWithResults(client_to_server, server_to_client):
    RED = 32
    BLUE = 94
    GREEN = 67
    WHITE = 1153
    GUMP_ID = 878787
    
    gd = Gumps.CreateGump(closable=True, movable=True) 
    Gumps.AddPage(gd, 0)

    Gumps.AddBackground(gd, 0, 0, 780, 550, 30546)
    Gumps.AddLabel(gd, 10, 10, BLUE, f'Packet Monitor ({TIMER}ms)')

    def DrawList(list_name, packet_list, x_offset):
        total_packets = sum(p['count'] for p in packet_list)
        total_size = sum(p['size'] for p in packet_list)
        bps = total_size / TIMER * 1000

        Gumps.AddLabel(gd, x_offset, 45, BLUE, f'{list_name}')
        Gumps.AddLabel(gd, x_offset, 70, WHITE, f'Packets: {total_packets}')
        Gumps.AddLabel(gd, x_offset, 85, WHITE, f'Bytes: {total_size}')
        Gumps.AddLabel(gd, x_offset, 100, RED, f'Bytes per second: {bps:.2f}')

        Gumps.AddLabel(gd, x_offset, 140, BLUE, f'Top 25 Packets')
        Gumps.AddLabel(gd, x_offset+250, 140, BLUE, f'Count')
        Gumps.AddLabel(gd, x_offset+300, 140, BLUE, f'Bytes')
        for i, packet in enumerate(packet_list[:25]):
            packet_name = UO_PACKETS_NAMES[packet['packet_id']] if packet['packet_id'] in UO_PACKETS_NAMES else '???'
            Gumps.AddLabel(gd, x_offset, 155+i*15, WHITE, f"[{packet['packet_id']}] {packet_name}")
            Gumps.AddLabel(gd, x_offset+250, 155+i*15, WHITE, f"{packet['count']}")
            Gumps.AddLabel(gd, x_offset+300, 155+i*15, WHITE, f"{packet['size']}")

    DrawList('Client to Server:', client_to_server, 10)
    DrawList('Server to Client:', server_to_client, 430)
    Gumps.SendGump(GUMP_ID, Player.Serial, 50, 50, gd.gumpDefinition, gd.gumpStrings)
    

# Script
LogPackets()
client_to_server, server_to_client = ParseLoggedPackets()
client_to_server, server_to_client = list(client_to_server.values()), list(server_to_client.values())
client_to_server.sort(key=lambda packet: packet['size'], reverse=True)
server_to_client.sort(key=lambda packet: packet['size'], reverse=True)
DrawGumpWithResults(client_to_server, server_to_client)
