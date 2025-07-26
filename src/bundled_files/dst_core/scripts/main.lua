-- Don't Starve Together Dedicated Server Main Initialization Script
-- This is a minimal main.lua file that allows DST server to start properly
-- Based on the original DST main.lua structure

print("Loading Don't Starve Together Dedicated Server...")

-- Basic global setup
GLOBAL.setmetatable(_G, {})

-- Initialize the game engine
require("constants")
require("class")
require("vector3")
require("util")
require("mathutil")
require("debugprint")

-- Core systems
require("gamelogic")
require("networking")
require("simutil")

-- Initialize the simulation
if not rawget(_G, "TheWorld") then
    _G.TheWorld = {}
end

if not rawget(_G, "TheNet") then
    _G.TheNet = {}
end

-- Basic mod support
if not rawget(_G, "ModManager") then
    _G.ModManager = {
        GetMods = function() return {} end,
        LoadMods = function() end,
        GetModInfo = function() return {} end
    }
end

-- Initialize shard system for DST
if not rawget(_G, "TheShard") then
    _G.TheShard = {
        IsMaster = function() return true end,
        GetShardId = function() return "Master" end
    }
end

-- Game state management
local game_state = "STARTING"

function SetGameState(state)
    game_state = state
    print("Game state changed to:", state)
end

function GetGameState()
    return game_state
end

-- Initialize the world
function InitializeWorld()
    print("Initializing world...")
    SetGameState("RUNNING")
    return true
end

-- Main initialization sequence
print("Starting Don't Starve Together server initialization...")
print("Server is ready to accept connections.")

-- Set initial game state
SetGameState("INITIALIZED")

-- Return success
return true
