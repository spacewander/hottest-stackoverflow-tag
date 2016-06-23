local utils = require './utils'
local is_iso_time = utils.is_iso_time
local is_postive = utils.is_postive
local raise_bad_request = utils.raise_bad_request
local json_response = utils.json_response
local Rank = require './rank'

local date = ngx.var.date
local N = tonumber(ngx.req.get_uri_args(1)['rank'])
if not is_iso_time(date) then
    raise_bad_request(
        "given date should be in ISO date format and between [2000, 2099].")
end
if not is_postive(N) then
    raise_bad_request(
        "'rank' argument should be postive.")
end
local res = Rank:new(N):in_the(date)
json_response(res)
