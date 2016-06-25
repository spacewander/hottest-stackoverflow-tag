use Test::Nginx::Socket::Lua 'no_plan';
use Cwd qw(cwd);

my $pwd = cwd();
our $HttpConfig = qq{
    lua_package_path "$pwd/src/?.lua;;";
};
our $Config = qq{
    location ~ ^/tag/(.+) {
        set \$tag_name \$1;
        content_by_lua_file $pwd/src/tag_api.lua;
    }
};

run_tests();

__DATA__
=== TEST 1: /tag/tagX ok
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- request
GET /tag/lua?from=2016-01-01&to=2016-01-04
--- response_body
{"data":{"2016-01-01":"1234","2016-01-02":"1300"}}

=== TEST 2: /tag/tagX requires argument 'from' and 'to'
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /tag/lua?from=2016-01-01',
'GET /tag/lua?to=2016-01-01']
--- error_code eval: [400, 400]

=== TEST 3: 'from' and 'to' should follow 'yyyy-mm-dd' format
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /tag/lua?from=2016-01-1&to=2016-01-04',
'GET /tag/lua?from=2016-01-01&to=2016-01-043']
--- error_code eval: [400, 400]

=== TEST 4: 'from' and 'to' should be in the 21th century
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /tag/lua?from=1999-01-01&to=2016-01-04',
'GET /tag/lua?from=2016-01-01&to=2100-01-04']
--- error_code eval: [400, 400]

=== TEST 5: 'tag_name' should be unescaped
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- request
GET /tag/c%23?from=2016-01-01&to=2016-01-04
--- response_body
{"data":{"2016-01-01":"6170","2016-01-02":"9170"}}

=== TEST 6: 'tag_name' should not contain whitespace
--- http_config eval: $::HttpConfig
--- config eval: $::Config
--- pipelined_requests eval
['GET /tag/aa%20space?from=2016-01-01&to=2016-01-04',
'GET /tag/aa%09tab?from=2016-01-01&to=2016-01-04']
--- error_code eval: [400, 400]
