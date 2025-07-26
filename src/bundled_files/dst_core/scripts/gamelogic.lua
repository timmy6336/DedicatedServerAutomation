-- Don't Starve Together Game Logic
-- Core game logic and world management

print("Initializing game logic...")

-- Game state manager
GameLogic = Class(function(self)
    self.world_state = "LOADING"
    self.day_cycle_time = 0
    self.season = "autumn"
    self.players = {}
end)

function GameLogic:Update(dt)
    -- Basic game loop update
    self.day_cycle_time = self.day_cycle_time + dt
    
    -- Simple day/night cycle (8 minutes per day)
    local day_length = 480
    if self.day_cycle_time >= day_length then
        self.day_cycle_time = 0
        self:OnNewDay()
    end
end

function GameLogic:OnNewDay()
    print("New day started")
    -- Broadcast new day to all players
    if TheNet then
        TheNet:BroadcastMessage("new_day", {day = self:GetDay()})
    end
end

function GameLogic:GetDay()
    return math.floor(os.time() / 480) + 1
end

function GameLogic:GetSeason()
    return self.season
end

function GameLogic:SetWorldState(state)
    self.world_state = state
    print("World state changed to:", state)
end

function GameLogic:GetWorldState()
    return self.world_state
end

-- Player management
function GameLogic:AddPlayer(player_id, player_data)
    self.players[player_id] = player_data
    print("Player added to game logic:", player_id)
end

function GameLogic:RemovePlayer(player_id)
    self.players[player_id] = nil
    print("Player removed from game logic:", player_id)
end

function GameLogic:GetPlayers()
    return self.players
end

-- World generation and management
function GameLogic:GenerateWorld()
    print("Generating world...")
    self:SetWorldState("GENERATING")
    
    -- Simulate world generation
    print("Creating world terrain...")
    print("Spawning resources...")
    print("Setting up biomes...")
    
    self:SetWorldState("GENERATED")
    print("World generation complete")
    return true
end

function GameLogic:StartWorld()
    print("Starting world...")
    if self.world_state == "GENERATED" then
        self:SetWorldState("RUNNING")
        print("World is now running")
        return true
    else
        print("Cannot start world - not properly generated")
        return false
    end
end

-- Initialize global game logic
if not rawget(_G, "TheWorld") then
    _G.TheWorld = GameLogic()
end

-- Utility functions
function GetWorldDay()
    if TheWorld then
        return TheWorld:GetDay()
    end
    return 1
end

function GetWorldSeason()
    if TheWorld then
        return TheWorld:GetSeason()
    end
    return "autumn"
end

print("Game logic initialized successfully.")

return true
