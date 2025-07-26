-- Don't Starve Together Constants
-- Essential constants for DST server operation

-- Game version and build info
DONT_STARVE_TOGETHER = true
PLATFORM = "WIN32_DEDICATED"
CONFIGURATION = "RELEASE"

-- Game modes
GAMEMODE = 
{
    SURVIVAL = "survival",
    WILDERNESS = "wilderness", 
    ENDLESS = "endless"
}

-- Network constants
NETWORK_TICK_RATE = 15
MAX_PLAYERS = 64

-- Shard types
SHARD_TYPE = 
{
    MASTER = "master",
    CAVES = "caves"
}

-- World settings
WORLD_SETTINGS = 
{
    DAY_TIME = 240,
    DUSK_TIME = 120,
    NIGHT_TIME = 240
}

-- Basic entity categories
COLLISION = 
{
    GROUND = 1,
    WORLD = 2,
    GIANTS = 4,
    CHARACTERS = 8,
    FLYERS = 16,
    ITEMS = 32,
    OBSTACLES = 64,
    SMALLOBSTACLES = 128,
    STRUCTURES = 256
}

-- Tags for entity classification
TAGS = 
{
    "player",
    "character", 
    "monster",
    "animal",
    "structure",
    "item",
    "food",
    "tool",
    "weapon"
}

return true
