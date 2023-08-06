"""
Easiest way to make tons of get/post requests with aiohttp.
You need DIY to get/post with different proxy/headers/cookies, or delete/patch/put request.

Supporting for more libs might be on the way.
    http.client / httplib
    urllib
    urllib3
    httpx
    grequests

Learn more about aiohttp: https://docs.aiohttp.org
Easy test with libs above: https://github.com/wangyi041228/http_libs_test
"""
__all__ = ['aio', 'proxy0', 'header0']

proxy0 = 'http://127.0.0.1:10080'
ua0 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
header0 = {
    'User-Agent': ua0,
    'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
    'Accept-Charset': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept-Encoding': 'gzip',
}
