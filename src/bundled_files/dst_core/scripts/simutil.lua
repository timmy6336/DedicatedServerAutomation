-- Simulation utilities for DST

-- Basic simulation state
SimulationState = {
    STOPPED = 0,
    RUNNING = 1,
    PAUSED = 2
}

local sim_state = SimulationState.STOPPED
local sim_time = 0

function SetSimulationState(state)
    sim_state = state
    print("Simulation state changed to:", state)
end

function GetSimulationState()
    return sim_state
end

function GetSimTime()
    return sim_time
end

function UpdateSimulation(dt)
    if sim_state == SimulationState.RUNNING then
        sim_time = sim_time + dt
        
        -- Update world if it exists
        if TheWorld and TheWorld.Update then
            TheWorld:Update(dt)
        end
    end
end

-- Entity management
local entities = {}
local next_entity_id = 1

function SpawnEntity(prefab_name, x, y, z)
    local entity = Entity()
    entity.prefab = prefab_name
    entity:SetPosition(x or 0, y or 0, z or 0)
    entity.entity_id = next_entity_id
    
    entities[next_entity_id] = entity
    next_entity_id = next_entity_id + 1
    
    print("Spawned entity:", prefab_name, "at", x, y, z)
    return entity
end

function RemoveEntity(entity_id)
    if entities[entity_id] then
        entities[entity_id] = nil
        print("Removed entity:", entity_id)
        return true
    end
    return false
end

function GetEntity(entity_id)
    return entities[entity_id]
end

function GetAllEntities()
    return entities
end

-- World utility functions
function FindEntitiesWithTag(tag, x, y, radius)
    local found = {}
    
    for id, entity in pairs(entities) do
        if entity:HasTag(tag) then
            if not x or not y or not radius then
                table.insert(found, entity)
            else
                local ex, ey, ez = entity:GetPosition()
                local dist = math.distance(x, y, ex, ey)
                if dist <= radius then
                    table.insert(found, entity)
                end
            end
        end
    end
    
    return found
end

-- Initialize simulation
function StartSimulation()
    print("Starting simulation...")
    SetSimulationState(SimulationState.RUNNING)
    
    if TheWorld and TheWorld.GenerateWorld then
        TheWorld:GenerateWorld()
        TheWorld:StartWorld()
    end
    
    print("Simulation started successfully")
end

function StopSimulation()
    print("Stopping simulation...")
    SetSimulationState(SimulationState.STOPPED)
    print("Simulation stopped")
end

return true
