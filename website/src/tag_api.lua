local json = require 'cjson.safe'
local json_encode = json.encode
local utils = require './utils'
local is_iso_time = utils.is_iso_time
local raise_bad_request = utils.raise_bad_request
local Tag = require './tag'

local args = ngx.req.get_uri_args(2)
local from = args['from']
local to = args['to']
if not is_iso_time(from) then
    raise_bad_request("'from' argument should be in ISO date format.")
end
if not is_iso_time(to) then
    raise_bad_request("'to' argument should be in ISO date format.")
end

local tags = Tag.new(ngx.var.tag_name).between(from, to)
res, err = json_encode(tags)
if res ~= nil then
    ngx.say(res)
else
    raise_bad_request(err)
end
