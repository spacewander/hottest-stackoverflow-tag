local redis = require 'resty.redis'
local utils = require './utils'
local time_fmt_to_num = utils.time_fmt_to_num


local _M = {}
local mt = {__index = _M}

function _M:new(num)
    local red = redis:new()
    red:set_timeout(1000)
    local ok, err = red:connect('127.0.0.1', 6379)
    if not ok then
        ngx.log(ngx.ERR, 'failed to connect: ', err)
        return nil
    end
    return setmetatable({redis = red, num = num}, mt)
end

-- date:yymmdd is zset{tag: number}

function _M.in_the(self, date)
    date = time_fmt_to_num(date)
    local raw, err = self.redis:zrevrange(
        'date:'..date, 0, self.num - 1, 'withscores')
    if not err then
        local results = {}
        for i = 1, #raw, 2 do
            results[raw[i]] = raw[i+1]
        end
        return results
    else
        ngx.log(ngx.ERR, 'failed to get data in given date: ', err)
        return {}
    end
end


return _M
