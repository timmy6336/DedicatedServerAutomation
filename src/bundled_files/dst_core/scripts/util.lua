-- Don't Starve Together Utility Functions
-- Essential utility functions for DST server

-- Math utilities
function Lerp(a, b, t)
    return a + (b - a) * t
end

function Clamp(val, min, max)
    if val < min then return min end
    if val > max then return max end
    return val
end

function Remap(val, oldMin, oldMax, newMin, newMax)
    return newMin + (val - oldMin) * (newMax - newMin) / (oldMax - oldMin)
end

-- Table utilities
function shallowcopy(orig)
    local copy = {}
    for orig_key, orig_value in pairs(orig) do
        copy[orig_key] = orig_value
    end
    return copy
end

function deepcopy(orig)
    local copy = {}
    for orig_key, orig_value in pairs(orig) do
        if type(orig_value) == "table" then
            copy[orig_key] = deepcopy(orig_value)
        else
            copy[orig_key] = orig_value
        end
    end
    return copy
end

function table.contains(table, element)
    for _, value in pairs(table) do
        if value == element then
            return true
        end
    end
    return false
end

-- String utilities
function string.starts(str, start)
    return string.sub(str, 1, string.len(start)) == start
end

function string.ends(str, ending)
    return ending == "" or string.sub(str, -string.len(ending)) == ending
end

-- File utilities
function file_exists(name)
    local f = io.open(name, "r")
    if f ~= nil then
        io.close(f)
        return true
    else
        return false
    end
end

-- Random utilities
function GetRandomMinMax(min, max)
    return min + math.random() * (max - min)
end

function GetRandomWithVariance(base, variance)
    return base + GetRandomMinMax(-variance, variance)
end

-- Time utilities
function GetTime()
    return os.time()
end

function GetTimeString()
    return os.date("%Y-%m-%d %H:%M:%S")
end

-- Debug utilities
function PrintTable(t, indent)
    indent = indent or 0
    local spacing = string.rep("  ", indent)
    
    for k, v in pairs(t) do
        if type(v) == "table" then
            print(spacing .. tostring(k) .. ":")
            PrintTable(v, indent + 1)
        else
            print(spacing .. tostring(k) .. ": " .. tostring(v))
        end
    end
end

-- Safe require function
function SafeRequire(module)
    local success, result = pcall(require, module)
    if success then
        return result
    else
        print("Warning: Could not load module", module, "Error:", result)
        return nil
    end
end

print("Utility functions loaded successfully.")

return true
