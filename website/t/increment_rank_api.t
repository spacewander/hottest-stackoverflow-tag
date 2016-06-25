use Test::Nginx::Socket::Lua 'no_plan';
use Cwd qw(cwd);

my $pwd = cwd();
our $HttpConfig = qq{
    lua_package_path "$pwd/src/?.lua;;";
};
our $Config = qq{
    location = /rank {
        content_by_lua_file $pwd/src/increment_rank_api.lua;
    }
};

run_tests();

__DATA__
=== TEST 1: /rank ok
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- request
GET /rank?from=2016-01-01&to=2016-01-02&rank=10
--- response_body
{"data":[["c#",3000],["python",660],["lua",66]]}

=== TEST 2: 'from', 'to', 'rank' are required
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /rank?to=2016-01-02&rank=10',
'GET /rank?from=2016-01-01&rank=10',
'GET /rank?from=2016-01-01&to=2016-01-02']
--- error_code eval: [400, 400, 400]

=== TEST 3: 'from', 'to' should follow 'yyyy-mm-dd' format
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /rank?from=2016-01-020&to=2016-01-02&rank=10',
'GET /rank?from=2016-01-01&to=2016-01-2&rank=10']
--- error_code eval: [400, 400]

=== TEST 4: 'from', 'to' should be in the 21th century
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /rank?from=1999-01-02&to=2016-01-02&rank=10',
'GET /rank?from=2016-01-01&to=2100-01-04&rank=10']
--- error_code eval: [400, 400]

=== TEST 5: 'rank' should be positive integer
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /rank?from=2016-01-01&to=2016-01-02&rank=-1',
'GET /rank?from=2016-01-01&to=2016-01-02&rank=2.5']
--- error_code eval: [400, 400]

=== TEST 6: data not found in specific date
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /rank?from=2015-01-02&to=2016-01-02&rank=10',
'GET /rank?from=2016-01-01&to=2016-01-04&rank=10']
--- error_code eval: [404, 404]
