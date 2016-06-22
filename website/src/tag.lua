local redis = require 'resty.redis'
local utils = require './utils'
local time_fmt_to_num = utils.time_fmt_to_num
local num_to_time_fmt = utils.num_to_time_fmt


local _M = {}
local mt = { __index = _M }

function _M:new(tag_name)
    local red = redis:new()
    red:set_timeout(1000) -- 1 sec
    local ok, err = red:connect('127.0.0.1', 6379)
    if not ok then
        ngx.log(ngx.ERR, 'failed to connect: ', err)
        return nil
    end
    return setmetatable({redis = red, tag_name = tag_name}, mt)
end

function _M.between(self, from, to)
    from = time_fmt_to_num(from)
    to = time_fmt_to_num(to)
    -- tag:xx is zset{'date:number': date}. For example, '160101:2000': 160101.
    local raw, err = self.redis:zrangebyscore('tag:'..self.tag_name, from, to)
    if not err then
        local results = {}
        for i = 1, #raw do
            fmt = num_to_time_fmt(string.sub(raw[i], 1, 6))
            results[fmt] = string.sub(raw[i], 8)
        end
        return results
    else
        ngx.log(ngx.ERR, 'failed to get redis data: ', err)
        return {}
    end
end


return _M
