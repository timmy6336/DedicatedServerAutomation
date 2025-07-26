-- Don't Starve Together Class System
-- Basic class implementation for DST

function Class(base, ctor)
    local c = {}
    
    if base then
        for i, v in pairs(base) do
            c[i] = v
        end
        c._base = base
    end
    
    c.__index = c
    c._class = c
    
    local mt = {}
    mt.__call = function(class_tbl, ...)
        local obj = {}
        setmetatable(obj, c)
        if ctor then
            ctor(obj, ...)
        elseif base and base.ctor then
            base.ctor(obj, ...)
        end
        return obj
    end
    
    c.ctor = ctor
    c.is_a = function(self, klass)
        local m = getmetatable(self)
        while m do
            if m == klass then
                return true
            end
            m = m._base
        end
        return false
    end
    
    setmetatable(c, mt)
    return c
end

-- Basic Entity class for DST objects
Entity = Class(function(self)
    self.entity_id = tostring(math.random(100000, 999999))
    self.position = {x = 0, y = 0, z = 0}
    self.components = {}
    self.tags = {}
end)

function Entity:AddComponent(component_name)
    self.components[component_name] = true
    return self
end

function Entity:RemoveComponent(component_name)
    self.components[component_name] = nil
    return self
end

function Entity:HasComponent(component_name)
    return self.components[component_name] ~= nil
end

function Entity:AddTag(tag)
    table.insert(self.tags, tag)
    return self
end

function Entity:HasTag(tag)
    for _, t in ipairs(self.tags) do
        if t == tag then
            return true
        end
    end
    return false
end

function Entity:SetPosition(x, y, z)
    self.position.x = x or 0
    self.position.y = y or 0
    self.position.z = z or 0
    return self
end

function Entity:GetPosition()
    return self.position.x, self.position.y, self.position.z
end

print("Class system initialized successfully.")

return true
