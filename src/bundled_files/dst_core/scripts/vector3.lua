-- Vector3 class for 3D math operations

Vector3 = Class(function(self, x, y, z)
    self.x = x or 0
    self.y = y or 0
    self.z = z or 0
end)

function Vector3:__tostring()
    return string.format("(%f, %f, %f)", self.x, self.y, self.z)
end

function Vector3:Length()
    return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
end

function Vector3:LengthSq()
    return self.x * self.x + self.y * self.y + self.z * self.z
end

function Vector3:Normalize()
    local len = self:Length()
    if len > 0 then
        self.x = self.x / len
        self.y = self.y / len
        self.z = self.z / len
    end
    return self
end

function Vector3:Dot(other)
    return self.x * other.x + self.y * other.y + self.z * other.z
end

function Vector3:Cross(other)
    return Vector3(
        self.y * other.z - self.z * other.y,
        self.z * other.x - self.x * other.z,
        self.x * other.y - self.y * other.x
    )
end

function Vector3:__add(other)
    return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
end

function Vector3:__sub(other)
    return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
end

function Vector3:__mul(scalar)
    return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
end

-- Global constructor function
function VectorToPoint(v)
    return Vector3(v.x, v.y, v.z)
end

function Point(x, y, z)
    return Vector3(x, y, z)
end

return Vector3
