local utils = require './utils'
local is_iso_time = utils.is_iso_time
local raise_bad_request = utils.raise_bad_request
local json_response = utils.json_response
local Tag = require './tag'

local args = ngx.req.get_uri_args(2)
local from = args['from']
local to = args['to']
if from == nil or to == nil then
    raise_bad_request("argument 'from' or 'to' is missing.")
end
if not is_iso_time(from) then
    raise_bad_request(
        "'from' argument should be in ISO date format and between [2000, 2099].")
end
if not is_iso_time(to) then
    raise_bad_request(
        "'to' argument should be in ISO date format and between [2000, 2099].")
end

local res = Tag:new(ngx.var.tag_name):between(from, to)
json_response(res)
