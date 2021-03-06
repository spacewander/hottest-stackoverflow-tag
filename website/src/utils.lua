local json = require 'cjson.safe'
local json_encode = json.encode

local _M = {}

-- Only check if given format matched 'yyyy-mm-dd', don't require it to be a valid date.
-- By the way, this function requires the yyyy is in the 21th century.
function _M.is_iso_time(time_fmt)
    if time_fmt == nil then return false end
    m, err = ngx.re.match(time_fmt, '^20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]$')
    return m ~= nil
end

function _M.is_postive(num)
    return num ~= nil and num > 0 and math.floor(num) == num
end

function _M.raise_bad_request(msg)
    ngx.status = ngx.HTTP_BAD_REQUEST
    ngx.say(json_encode({
        error = msg,
        status_code = ngx.HTTP_BAD_REQUEST
    }))
    ngx.exit(ngx.OK)
end

-- convert time format as yyyy-mm-dd to num as yymmdd
function _M.time_fmt_to_num(time_fmt)
    s = string.sub(time_fmt, 3, 4)..string.sub(time_fmt, 6, 7)
            ..string.sub(time_fmt, 9)
    num = tonumber(s)
    return num
end

function _M.num_to_time_fmt(num)
    s = tostring(num)
    fmt = '20'..string.sub(s, 1, 2)..'-'..string.sub(s, 3, 4)..'-'
            ..string.sub(s, 5, 6)
    return fmt
end

function _M.vacant_data()
    ngx.status = ngx.HTTP_NOT_FOUND
    ngx.say(json_encode({
        error = "Data is vacant in specific date.",
        status_code = ngx.HTTP_NOT_FOUND
    }))
    ngx.exit(ngx.OK)
end

function _M.json_response(res)
    res = {data = res}
    res, err = json_encode(res)
    if res ~= nil then
        ngx.say(res)
    else
        _M.raise_bad_request(err)
    end
end

return _M
