-- Init data in redis before testing.
-- Usage: redis-cli --eval init_data.lua
redis.call('flushall')

local tags = {
    ['tag:lua'] = {
        ['160101:1234'] = 160101,
        ['160102:1300'] = 160102
    }
}
for name, tag in pairs(tags) do
    for member, score in pairs(tag) do
        redis.call('zadd', name, score, member)
    end
end

local dates = {
    ['date:160101'] = {
        lua = '1234',
        python = '12340'
    },
    ['date:160102'] = {
        lua = '1300',
        python = '13000'
    }
}
for name, date in pairs(dates) do
    for member, score in pairs(date) do
        redis.call('zadd', name, score, member)
    end
end
