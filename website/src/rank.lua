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
            table.insert(results, {raw[i], tonumber(raw[i+1])})
        end
        table.sort(results,
            function(first, second) return first[2] > second[2] end)
        return results
    else
        ngx.log(ngx.ERR, 'failed to get'..N..
            ' data in given date '..date..': ', err)
        return {}
    end
end

function _M.tag_pairs_in_the(self, date)
    date = time_fmt_to_num(date)
    local raw, err = self.redis:zrevrange(
        'date:'..date, 0, self.num - 1, 'withscores')
    if not err then
        local results = {}
        for i = 1, #raw, 2 do
            results[raw[i]] = tonumber(raw[i+1])
        end
        return results
    else
        ngx.log(ngx.ERR, 'failed to get'..N..
            ' data in given date '..date..': ', err)
        return {}
    end
end

function _M.between(self, from, to)
    local N = self.num
    if self.num <= 100 then
        self.num = 200
    elseif self.num <= 500 then
        self.num = 1000
    else
        self.num = self.num * 2
    end
    before = _M.tag_pairs_in_the(self, from)
    after = _M.tag_pairs_in_the(self, to)
    local raw = {}
    for tag, num in pairs(after) do
        if before[tag] ~= nil then
            raw[tag] = after[tag] - before[tag]
        end
    end

    local results = {}
    for tag, score in pairs(raw) do
        table.insert(results, {tag, score})
    end
    table.sort(results, function(first, second)
        return first[2] > second[2]
    end)

    local response = {}
    for i = 1, N do
        table.insert(response, results[i])
    end
    return response
end

return _M
