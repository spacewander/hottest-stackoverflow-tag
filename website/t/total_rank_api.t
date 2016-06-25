use Test::Nginx::Socket::Lua 'no_plan';
use Cwd qw(cwd);

my $pwd = cwd();
our $HttpConfig = qq{
    lua_package_path "$pwd/src/?.lua;;";
};
our $Config = qq{
    location ~ ^/rank/(20[0-9][0-9]-[0-1][0-9]-[0-3][0-9])\$ {
        set \$date \$1;
        content_by_lua_file $pwd/src/total_rank_api.lua;
    }
};

run_tests();

__DATA__
=== TEST 1: /rank/date ok
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- request
GET /rank/2016-01-01?rank=10
--- response_body
{"data":[["php",19880],["python",12340],["c#",6170],["lua",1234]]}

=== TEST 2: /rank/date requires argument 'rank'
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- request
GET /rank/2016-01-01
--- error_code: 400

=== TEST 3: 'date' should follow 'yyyy-mm-dd' format and be in the 21th century
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /rank/2016-01-011?rank=10',
'GET /rank/1999-01-01?rank=10',
'GET /rank/2100-01-04?rank=10']
--- error_code eval: [404, 404, 404]

=== TEST 4: 'rank' should be positive integer
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /rank/2016-01-01?rank=-1',
'GET /rank/2016-01-01?rank=1.5']
--- error_code eval: [400, 400]

=== TEST 5: data not found in specific date
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- request
GET /rank/2015-01-02?rank=10
--- error_code: 404
