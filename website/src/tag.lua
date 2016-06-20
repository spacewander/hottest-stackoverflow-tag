local _M = {}

local mt = { __index = _M }
function _M:new(tag_name)
    return setmetatable({tag_name = tag_name }, mt)
end

function _M.between(self, from, to)
    return {}
end


return _M
