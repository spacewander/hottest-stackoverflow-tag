local utils = require './utils'
local is_iso_time = utils.is_iso_time
local is_postive = utils.is_postive
local raise_bad_request = utils.raise_bad_request
local vacant_data = utils.vacant_data
local json_response = utils.json_response
local Rank = require './rank'

local args = ngx.req.get_uri_args(3)
local from = args['from']
local to = args['to']
local N = tonumber(args['rank'])
if not is_iso_time(from) then
    raise_bad_request(
        "'from' argument should be in ISO date format and between [2000, 2099].")
end
if not is_iso_time(to) then
    raise_bad_request(
        "'to' argument should be in ISO date format and between [2000, 2099].")
end
if not is_postive(N) then
    raise_bad_request(
        "'rank' argument should be postive.")
end
local res = Rank:new(N):between(from, to)
if #res == 0 then
    vacant_data()
end
json_response(res)
