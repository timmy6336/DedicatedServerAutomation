-- Debug print functionality for DST

local DEBUG_ENABLED = true

function print(...)
    if DEBUG_ENABLED then
        local args = {...}
        local output = ""
        
        for i, v in ipairs(args) do
            if i > 1 then
                output = output .. "\t"
            end
            output = output .. tostring(v)
        end
        
        -- Add timestamp
        local timestamp = os.date("[%H:%M:%S]")
        output = timestamp .. " " .. output
        
        -- Use native print
        io.write(output .. "\n")
        io.flush()
    end
end

function DebugPrint(...)
    if DEBUG_ENABLED then
        print("[DEBUG]", ...)
    end
end

function ErrorPrint(...)
    print("[ERROR]", ...)
end

function WarningPrint(...)
    print("[WARNING]", ...)
end

function InfoPrint(...)
    print("[INFO]", ...)
end

-- Set debug level
function SetDebugEnabled(enabled)
    DEBUG_ENABLED = enabled
end

return true
