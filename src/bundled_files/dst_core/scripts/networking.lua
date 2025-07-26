-- Don't Starve Together Networking System
-- Minimal networking functionality for DST server

print("Initializing networking system...")

-- Network message types
NETWORK_MESSAGES = {
    PLAYER_JOIN = "player_join",
    PLAYER_LEAVE = "player_leave", 
    WORLD_UPDATE = "world_update",
    CHAT_MESSAGE = "chat_message"
}

-- Network manager
NetworkManager = Class(function(self)
    self.connected_players = {}
    self.message_queue = {}
end)

function NetworkManager:SendMessage(player, message_type, data)
    -- Basic message sending functionality
    print("Sending message:", message_type, "to player:", player)
end

function NetworkManager:BroadcastMessage(message_type, data)
    -- Broadcast to all connected players
    print("Broadcasting message:", message_type)
    for player_id, player in pairs(self.connected_players) do
        self:SendMessage(player_id, message_type, data)
    end
end

function NetworkManager:OnPlayerJoin(player_id)
    print("Player joined:", player_id)
    self.connected_players[player_id] = {
        id = player_id,
        connected_time = os.time()
    }
    self:BroadcastMessage(NETWORK_MESSAGES.PLAYER_JOIN, {player_id = player_id})
end

function NetworkManager:OnPlayerLeave(player_id)
    print("Player left:", player_id)
    self.connected_players[player_id] = nil
    self:BroadcastMessage(NETWORK_MESSAGES.PLAYER_LEAVE, {player_id = player_id})
end

-- Initialize global network manager
if not rawget(_G, "TheNet") then
    _G.TheNet = NetworkManager()
end

-- Network utility functions
function SendNetworkMessage(player, msg_type, data)
    if TheNet then
        TheNet:SendMessage(player, msg_type, data)
    end
end

function BroadcastNetworkMessage(msg_type, data)
    if TheNet then
        TheNet:BroadcastMessage(msg_type, data)
    end
end

print("Networking system initialized successfully.")

return true
