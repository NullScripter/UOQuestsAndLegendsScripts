__version__ = "3.3"
from AutoComplete import *
import random

# Script to mine a whole cave/area.
# The script automatically move, mine, and search/queue nearby tiles to 
# mine. The accounts for the grid/vein size and if tile coloring is turned on,
# it will color queued to visit as green, mined tiles as red, and ignored tiles
# as yellow (a tile is ignored if a tile in the same vein was fully mined)


# Personal Settings (change it to yours)
ENABLE_TILE_COLORING = True

MINE_DIRT_TILES = False
MINE_SAND_TILES = False

# Regular Shovel = (0x0F39, 0), Garg Right (0x0E86, 0x076c)
SHOVEL_ID = 0x0F39 
SHOVEL_COLOR = 0


###################################################################
# Other settings (do not change unless you know what you are doing)
MINING_DELAY = 1200

class LandTile():
    def __init__(self, X, Y, Z, LandID, StaticID=None):
        self.X, self.Y, self.Z = X, Y, Z
        self.LandID = LandID
        self.StaticID = StaticID
        self.PseudoSerial = random.randint(0x40000000, 0x7FFFFFFF) # Item Serial Range
        self.InjectedColor = None

    def __hash__(self):
        return hash((self.X, self.Y))

    def __eq__(self, other):
        return self.X == other.X and self.Y == other.Y


def ColorClientTile(land_tile, color, max_distance=23):
    '''
    Send a packet to the client to create a copy a land tile of a specific color
    '''
    if abs(Player.Position.X - land_tile.X) > max_distance or abs(Player.Position.Y - land_tile.Y) > max_distance:
        land_tile.InjectedColor = None
        return 
    if land_tile.InjectedColor == color: return
    packet = [0xF3, 0x00, 0x01]  # Packet ID (3 byte)
    packet.extend([0x00])  # 0x00 = Item , 0x02 = Multi (1 byte)
    packet.extend(land_tile.PseudoSerial.to_bytes(4, byteorder='big'))  # Serial (4 bytes)
    packet.extend(land_tile.LandID.to_bytes(2, byteorder='big'))  # Graphic (2 bytes)
    packet.extend([0x00, 0x00, 0x01, 0x00, 0x01]) # Facing (1 byte), Amount#1 (2 bytes), Amount#2 (2 bytes)
    packet.extend(land_tile.X.to_bytes(2, byteorder='big'))  # X (2 bytes)
    packet.extend(land_tile.Y.to_bytes(2, byteorder='big'))  # Y (2 bytes)
    packet.extend(land_tile.Z.to_bytes(1, byteorder='big', signed=True))  # Z (1 bytes)
    packet.extend([0x1D])  # Layer (1 byte)
    packet.extend(color.to_bytes(2, byteorder='big'))  # Color (2 bytes)
    packet.extend([0x00, 0x00, 0x00])  # Flag (1 bytes), ??? (2 bytes?)
    PacketLogger.SendToClient(packet)
    land_tile.InjectedColor = color
    Misc.Pause(25)


def GetPlayerRealMaxWeight():
    '''
    Get the minimum between Player max weight and max weight of their Backpack  
    for cases where player Str becomes higher than the backpack.
    '''
    try:
        prop = [prop.ToString() for prop in Player.Backpack.Properties if 'Contents' in prop.ToString()][0]
        parts = [part.split('/') for part in prop.split(' ') if '/' in part]
        backpack_maxweight = int(parts[1][1])
        return min(Player.MaxWeight, backpack_maxweight)
    except:
        return Player.MaxWeight


def CollectItems(weight_factor=0.9):
    if Player.Weight < GetPlayerRealMaxWeight() * weight_factor: return
    Player.ChatSay(0x21, '[CollectItems')
    Misc.Pause(500)
    

def FindNearbyLandTilesByID(land_ids, radius=9):
    '''
    Find all tile coordinates around the player that matches any LandID in a list.
    '''
    startX, startY = Player.Position.X, Player.Position.Y,
    land_tiles = []
    for y in range(startY-radius, startY+radius+1):
        for x in range(startX-radius, startX+radius+1):
            land_id = Statics.GetLandID(x, y, Player.Map)
            if land_id is None:
                continue

            statics = Statics.GetStaticsTileInfo(x, y, Player.Map)
            if any(Statics.GetTileFlag(s.StaticID, 'Impassable') for s in statics):
                continue

            # Not in a cave
            if land_id in land_ids:
                z = Statics.GetLandZ(x, y, Player.Map)
                land_tiles.append(LandTile(x, y, z, 1305)) 
            # In a cave
            for s in statics:
                if s.StaticID in land_ids:
                    land_tiles.append(
                        LandTile(x, y, s.StaticZ, s.StaticID, s.StaticID))
                    break

    return land_tiles


# Script
def GoTo(X,Y):
    route = PathFinding.Route()
    route.X, route.Y = X, Y
    route.DebugMessage = False
    route.StopIfStuck = True
    PathFinding.Go(route)


def MineAllValidTiles():
    '''
    Mine all land tiles in cave.
    Starts at player position and queue new tiles to be mined as new tiles are visited.
    '''
    land_ids = {0x053B, 0x053C, 0x053D, 0x053E, 0x053F,
                0x0540, 0x0541, 0x0542, 0x0543, 0x0544, 0x0545, 0x0546, 0x0547, 0x0548, 0x0549, 0x054A, 0x054B, 0x054C, 0x054D, 0x054E, 0x054F,  
                0x0550, 0x0551, 0x0552, 0x0553, 0x056A, 
                0x0245, 0x0246, 0x0247, 0x0248, 0x0249}
    if MINE_SAND_TILES: land_ids.update({0x0016,0x0017,0x0018,0x0019})
    if MINE_DIRT_TILES: land_ids.update({0x0071, 0x0072, 0x0073, 0x0074, 0x0075, 0x0076, 0x0077, 0x0078})
    
    tiles_to_visit = FindNearbyLandTilesByID(land_ids, radius=0) #start with player position 
    tiles_visited = set()
    tiles_mined = set()

    if Target.HasTarget(): Target.Cancel()

    while len(tiles_to_visit) > 0:
        # Color tiles
        if ENABLE_TILE_COLORING:
            for t in tiles_to_visit: ColorClientTile(t, 70) # green
            for t in tiles_visited: ColorClientTile(t, 55) # yellow
            for t in tiles_mined:  ColorClientTile(t, 35) # red

        # Go to next spot
        next_spot = tiles_to_visit.pop()
        if next_spot in tiles_visited:
            continue

        GoTo(next_spot.X,next_spot.Y)

        # Mark same vein tiles as visited
        nearby_tiles = FindNearbyLandTilesByID(land_ids)
        tiles_visited.update(t for t in nearby_tiles if t.X//8 == next_spot.X//8 and t.Y//8==next_spot.Y//8)
        tiles_to_visit.extend(t for t in nearby_tiles if t not in tiles_visited)
        tiles_to_visit.sort(key=lambda t: (t.X-next_spot.X)**2 + (t.Y-next_spot.Y)**2, reverse=True)

        Player.HeadMessage(70, f'{len(tiles_to_visit)} to visit')
        Player.HeadMessage(55, f'{len(tiles_visited)} ignored')
        Player.HeadMessage(35, f'{len(tiles_mined)} mined')

        # Mine at current position
        while True:
            shovels = Items.FindAllByID(SHOVEL_ID, SHOVEL_COLOR, Player.Backpack.Serial, 1)
            if len(shovels) == 0: return Misc.SendMessage('ERROR: No shovel found. Stopping! ', 35)

            CollectItems()           
            if Player.Mount: Mobiles.UseMobile(Player.Serial)  # dismount

            Timer.Create('mining_max_delay', MINING_DELAY)
            Journal.Clear()
            Target.Cancel()
            for shovel in shovels:
                CollectItems()
                Items.UseItem(shovel)
                Target.WaitForTarget(MINING_DELAY)
                if Target.HasTarget():
                    if next_spot.StaticID is None:
                        Target.TargetExecute(next_spot.X, next_spot.Y, next_spot.Z)
                    else:
                        Target.TargetExecute(
                            next_spot.X, next_spot.Y, next_spot.Z, next_spot.StaticID)
                
                if not Timer.Check('mining_max_delay'): break
                if Journal.Search("There is no") or Journal.Search("mine that") or Journal.Search("be seen") or Journal.Search("no sand here") or Journal.Search("far away"):
                    break
            
            while Timer.Check('mining_max_delay') and not (Journal.Search("There is no") or Journal.Search("mine that") or Journal.Search("be seen") or Journal.Search("no sand here") or Journal.Search("far away")):
                Misc.Pause(100)

            if Journal.Search("There is no") or Journal.Search("mine that") or Journal.Search("be seen")  or Journal.Search("no sand here")  or Journal.Search("far away"):
                break
            else:
                tiles_mined.add(next_spot)
        

    Misc.Beep()
    Misc.SendMessage(f'{len(tiles_to_visit)} to visit', 70)
    Misc.SendMessage(f'{len(tiles_visited)} ignored', 55)
    Misc.SendMessage(f'{len(tiles_mined)} mined', 35)
    Misc.SendMessage('Stopping! All tiles were visited!', 170)


if __name__ == '__main__':
    MineAllValidTiles()
