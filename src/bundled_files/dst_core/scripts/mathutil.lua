-- Math utilities for DST

PI = math.pi
TWOPI = 2 * math.pi
DEGREES = 180 / math.pi
RADIANS = math.pi / 180

function deg2rad(degrees)
    return degrees * RADIANS
end

function rad2deg(radians)
    return radians * DEGREES
end

function math.sign(x)
    if x > 0 then
        return 1
    elseif x < 0 then
        return -1
    else
        return 0
    end
end

function math.round(x)
    return math.floor(x + 0.5)
end

function math.clamp(x, min, max)
    if x < min then return min end
    if x > max then return max end
    return x
end

function math.lerp(a, b, t)
    return a + (b - a) * t
end

function math.distance(x1, y1, x2, y2)
    local dx = x2 - x1
    local dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)
end

function math.distanceSq(x1, y1, x2, y2)
    local dx = x2 - x1
    local dy = y2 - y1
    return dx * dx + dy * dy
end

function math.angle(x1, y1, x2, y2)
    return math.atan2(y2 - y1, x2 - x1)
end

-- Random number utilities
function math.randomFloat(min, max)
    return min + math.random() * (max - min)
end

function math.randomChoice(table)
    if #table == 0 then return nil end
    return table[math.random(1, #table)]
end

return true
