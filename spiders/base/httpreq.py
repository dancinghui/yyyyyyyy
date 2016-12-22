#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

import pycurl
import urllib
import sys
import re
import threading
import time
import copy
import traceback
from StringIO import StringIO
from collections import OrderedDict
from spiders.base.runtime import Log
from cookielib import CookieJar, Cookie, DefaultCookiePolicy


class MyCookiePolicy(DefaultCookiePolicy):
    def __init__(self):
        DefaultCookiePolicy.__init__(self)

    def return_ok_expires(self, cookie, request):
        if cookie.expires == 0:
            return True
        if cookie.is_expired(0):
            return False

        return True

class CurlCookieJar(CookieJar):


    class FakeReq(object):
        def __init__(self, domain, path):
            self._domain = domain
            self._path = path
        def get_full_url(self):
            return "https://%s%s" % (self._domain, self._path)
        def is_unverifiable(self):
            return False
        def get_header(self, name, defv=''):
            if name.lower() == 'host':
                return self._domain
            return defv
        def get_type(self):
            return 'https'

    def __init__(self, ignore_expires=True, ignore_discard=True):
        CookieJar.__init__(self, policy=MyCookiePolicy())
        self._ignore_expires = ignore_expires
        self._ignore_discard = ignore_discard


    def add_list(self, cks):
        assert isinstance(cks, list)
        if not cks:
            return
        for ck in cks:
            if isinstance(ck, str):
                self.add_line(ck)
            elif isinstance(ck, unicode):
                self.add_line(ck.encode('utf-8'))
            elif isinstance(ck, Cookie):
                self.set_cookie(ck)
            else:
                raise RuntimeError("type error, support string list and cookie list.")

    def add_line(self, line):
        domain, domain_specified, path, secure, expires, name, value = line.split('\t')
        return self._add_cookie(domain, name, value, domain_specified, path, secure, expires)


    def _add_cookie(self, domain, name, value, domain_specified="FALSE", path="/", secure="FALSE", expires=0):
        secure = (secure == "TRUE")
        domain_specified = (domain_specified == "TRUE")
        if name == "":
            # cookies.txt regards 'Set-Cookie: foo' as a cookie
            # with no name, whereas cookielib regards it as a
            # cookie with no value.
            name = value
            value = None

        initial_dot = domain.startswith(".")
        # assert domain_specified == initial_dot
        discard = False
        if expires == "":
            expires = None
            discard = True

        # assume path_specified is false
        c = Cookie(0, name, value,
                   None, False,
                   domain, domain_specified, initial_dot,
                   path, False,
                   secure,
                   expires,
                   discard,
                   None,
                   None,
                   {})
        if not self._ignore_discard and c.discard:
            #a session cookie
            #TODO deal with a session cookie
            pass
        if not self._ignore_expires and c.is_expired():
            #end of life, do not add it
            raise RuntimeError("the cookie's life ended, try add it in ignore_expires mod.")

        self.set_cookie(c)
        return

    def get_cookie(self, domain, path, cookie_name):
        rq = CurlCookieJar.FakeReq(domain, path)
        if len(domain) > 0:
            cookies = self._cookies_for_request(rq)
            for ck in cookies:
                if ck.name == cookie_name:
                    return ck
        else:
            # when there is no domain, also ignores path.
            for k1, v1 in self._cookies.items():
                for k2, v2 in v1.items():
                    if v2.has_key(cookie_name):
                        return v2[cookie_name]
        return None

    def get_value(self, cookie_domain, cookie_path, cookie_name):
        ck = self.get_cookie(cookie_domain, cookie_path, cookie_name)
        if not ck:
            return None
        return ck.value

    def get_all_value(self, cookie_name):
        reslist=[]
        for k1, v1 in self._cookies.items():
            if v1 is not None:
                for k2, v2 in v1.items():
                    r = v2.get(cookie_name, None)
                    if r is not None:
                        reslist.append(r.value)

        if len(reslist) is 0:
            raise RuntimeError("No such cookie named '%s'" % cookie_name)
        if len(reslist) is 1:
            return reslist[0]
        return reslist

    def __str__(self):
        return self._cookies.__str__()


class DNSError(Exception):
    def __init__(self, r):
        Exception.__init__(self)
        self.hostname = r

    def __str__(self):
        return "Dns failed:" + self.hostname


class ProxyError(Exception):
    def __init__(self, r):
        Exception.__init__(self)
        self.reason = r

    def __str__(self):
        return "ProxyError:%s" % self.reason


class CurlReq(object):
    DEBUGREQ = 1

    class Request(object):
        def __init__(self):
            self.headers = None
            self.url = None

    class Response(object):
        def __init__(self):
            self.content = None
            self.text = None
            self.encoding = None
            self.code = 0
            self.request = CurlReq.Request()
            self.cookies = None
            self.headers = None

    def __init__(self, curlshare):
        self.curl = None
        self.curl_response = None
        self._curlshare = curlshare
        self.reset()
        self.otherinfo = {}
        self._proxy = ''
        self._buffer = None
        self._user_agent = 'curl/7.20.1'

    def __del__(self):
        if self.curl:
            self.curl.close()

    def reset(self):
        if self.curl:
            self.curl.close()
        self.curl = pycurl.Curl()

        if self._curlshare:
            self.curl.setopt(pycurl.SHARE, self._curlshare)

    def _debug_func(self, _type, text):
        r = self.curl_response
        if r:
            if _type == pycurl.INFOTYPE_HEADER_OUT:
                r.request.headers = text
            elif _type == pycurl.INFOTYPE_HEADER_IN:
                r.headers = (r.headers or '') + text
            else:
                pass

    def _inner_reset(self):
        c = self.curl
        c.reset()
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 7)
        c.setopt(pycurl.NOSIGNAL, 1)
        c.setopt(pycurl.VERBOSE, 1)
        c.setopt(pycurl.DEBUGFUNCTION, self._debug_func)
        c.setopt(pycurl.ENCODING, 'gzip, deflate')
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
        return c

    def select_user_agent(self, ua):
        if ua == 'baidu':
            self._user_agent = 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'
        elif ua == 'firefox':
            self._user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:42.0) Gecko/20100101 Firefox/42.0'
        elif ua[0:1] == '=':
            self._user_agent = ua[1:]
        else:
            raise RuntimeError("unknown user agent")

    def _gen_kv_info(self, params):
        if isinstance(params, unicode):
            return params.encode('utf-8')
        if isinstance(params, str):
            return params

        if isinstance(params, dict):
            qstr = ''
            for k, v in params.items():
                if isinstance(k, unicode):
                    k = k.encode("utf-8")
                if isinstance(v, unicode):
                    v = v.encode('utf-8')

                qstr += '&%s=%s' % (urllib.quote(str(k)), urllib.quote(str(v)))

            return qstr[1:]
        else:
            return ''

    def prepare_req(self, url, **kwargs):
        c = self._inner_reset()
        c.setopt(pycurl.TIMEOUT, int(kwargs.get('timeout',30)))
        rv = CurlReq.Response()
        self.curl_response = rv
        self._buffer = StringIO()
        c.setopt(pycurl.WRITEDATA, self._buffer)

        headers = kwargs.get('headers', {})
        if not 'User-Agent' in headers.keys():
            headers['User-Agent'] = self._user_agent
        header_tuples = [str('%s: %s' % x) for x in headers.items()]
        c.setopt(pycurl.HTTPHEADER, header_tuples)

        allow_redirect = kwargs.get('allow_redirects', None)
        if allow_redirect:
            c.setopt(pycurl.FOLLOWLOCATION, 1)
        else:
            c.setopt(pycurl.FOLLOWLOCATION, 0)

        params = kwargs.get('params')
        if params:
            qstr = self._gen_kv_info(params)
            if '?' in url:
                url += '&' + qstr
            else:
                url += '?' + qstr

        c.setopt(pycurl.URL, url)

        files = kwargs.get('files')
        if files:
            ifile = 0
            file_fields = []
            for name, v_ in files.items():
                if isinstance(v_, tuple):
                    filename, fileobj = v_
                else:
                    fileobj = v_
                    if ifile > 0:
                        filename = 'file%d' % ifile
                    else:
                        filename = 'file'

                ifile += 1
                if isinstance(fileobj, str):
                    value = pycurl.FORM_BUFFER, filename, pycurl.FORM_BUFFERPTR, fileobj

                else:
                    fileobj.seek(0)
                    value = pycurl.FORM_BUFFER, filename, pycurl.FORM_BUFFERPTR, fileobj.read()
                    fileobj.seek(0)

                file_fields.append((name, value))

            for name, v_ in kwargs.get('data', {}).items():
                file_fields.append((name, str(v_)))
            c.setopt(pycurl.HTTPPOST, file_fields)
        else:
            data = kwargs.get('data', None)
            if data is not None:
                c.setopt(pycurl.POSTFIELDS, self._gen_kv_info(data))

        auth = kwargs.get('auth')
        if auth:
            c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
            c.setopt(pycurl.USERNAME, auth[0])
            c.setopt(pycurl.PASSWORD, auth[1])

        pr = kwargs.get('proxies', None)
        setproxy = None

        if pr:
            setproxy = pr.get('https')
            c.setopt(pycurl.PROXY, setproxy)
        self._proxy = setproxy
        return c

    def doreq(self, url, **kwargs):
        c = self.prepare_req(url, **kwargs)
        try:
            if CurlReq.DEBUGREQ:
                sys.stderr.write("req.url: " + url)
                if 'data' in kwargs:
                    sys.stderr.write(' data: ' + kwargs.get('data'))

                sys.stderr.write(" proxy: " + str(self._proxy) + "\n")

            c.perform()

        except pycurl.error as e:
            code, msg = e.args
            errorobj = self._error_obj(code, msg)
            if errorobj:
                raise errorobj
            else:
                raise

        rv = self._build_result()
        c.reset()
        return rv

    def _error_obj(self, code, msg):
        setproxy = self._proxy
        rv = self.curl_response
        m = re.search("Couldn't resolve host '(.*?)'", msg)

        if m:
            return DNSError(m.group(1))

        if setproxy:
            # 检查哪些是由代理服务器导致的问题.
            m = re.search(r'(\d+\.\d+\.\d+\.\d+)', setproxy)
            prhost = m.group(1) if m else '1111.1111.2222.3333'
            if code == pycurl.E_COULDNT_CONNECT and prhost in msg:
                return ProxyError(msg)

            elif code == pycurl.E_OPERATION_TIMEDOUT:
                if 'connection timed out' in msg.lower():
                    return ProxyError(msg)
                if re.search(r'Operation timed out .* with 0 bytes received', msg, re.I):
                    return ProxyError(msg)
            elif code == pycurl.E_RECV_ERROR:
                if not rv.headers:
                    return ProxyError(msg)

    def _build_result(self):
        c = self.curl
        rv = self.curl_response
        rv.content = self._buffer.getvalue()
        if re.search('Content-Type:.*charset=utf-8', rv.headers, re.M | re.I):
            rv.encoding = 'utf-8'
        elif re.search('Content-Type.*(gbk|gb2312)', rv.content, re.M | re.I):
            rv.encoding = 'gb18030'
        else:
            rv.encoding = 'utf-8'
        rv.text = rv.content.decode(rv.encoding, 'replace')
        rv.code = c.getinfo(c.RESPONSE_CODE)
        rv.cookies = c.getinfo(c.INFO_COOKIELIST)
        rv.request.url = c.getinfo(c.EFFECTIVE_URL)
        return rv


class BasicRequests(object):
    def __init__(self):
        self.locker = threading.RLock()
        self.sp_proxies = OrderedDict()
        self._auto_change_proxy = False
        self._cur_proxy_index = -1
        self.default_headers = {}
        self._curltls = threading.local()
        self._user_agent = 'curl/7.45.0'
        self.select_user_agent('baidu')

    def select_user_agent(self, ua):
        if ua == 'baidu':
            self._user_agent = 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'
        elif ua == 'firefox':
            self._user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:42.0) Gecko/20100101 Firefox/42.0'
        elif ua[0:1] == '=':
            self._user_agent = ua[1:]
        else:
            raise RuntimeError("unknown user agent")


    def compose_url(self, url, name, value):
        assert isinstance(url, (unicode, str))
        if isinstance(url, unicode):
            url = url.encode('utf-8')

        m = re.search("[?&]%s=([^&]*)" % name, url)
        if m:
            return url[0:m.start(1)] + value + url[m.end(1):]
        else:
            return "%s&%s=%s" % (url, name, value)

    def set_proxy(self, prs, index=-1, auto_change=True):
        self._cur_proxy_index = index
        self._auto_change_proxy = auto_change

        if isinstance(prs, list):
            for p in prs:
                self.sp_proxies[p] = 0
        elif isinstance(prs, str) or isinstance(prs, unicode):
            self.sp_proxies[prs] = 0
        else:
            raise RuntimeError('invalid argument')

    def load_proxy(self, fn, index=-1, auto_change=True):
        with open(fn, 'r') as f:
            for line in f:
                line = line.strip()
                line = re.sub('\s*#.*','',line)
                if not line:
                    continue
                self.sp_proxies[line] = 0
        self._cur_proxy_index = index
        self._auto_change_proxy = auto_change
        print "[============== %d proxy loaded ===============]" % len(self.sp_proxies.keys())

    def _set_proxy(self, kwargs, selproxy):
        m = re.match('([0-9.]+):(\d+):([a-z0-9]+):([a-z0-9._-]+)$', selproxy, re.I)
        m1 = re.match('([0-9.]+):(\d+):([a-z0-9]+)$', selproxy, re.I)

        if m:
            prstr = '%s:%s@%s:%s' % (m.group(3), m.group(4), m.group(1), m.group(2))
            proxies = {'http': 'http://' + prstr, 'https': 'https://' + prstr}
            kwargs['proxies'] = proxies
        elif m1:
            prstr = '%s:%s' % (m1.group(1), m1.group(2))
            proxies = {'http': 'http://' + prstr, 'https': 'https://' + prstr}
            kwargs['auth'] = ('PROXY_PASSWORD', m1.group(3))
            kwargs['proxies'] = proxies
        else:
            proxies = {'http': 'http://' + selproxy, 'https': 'https://' + selproxy}
            kwargs['proxies'] = proxies

    def _replace_proxy(self, kwargs, memo):
        with self.locker:
            if not isinstance(self.sp_proxies, dict) or len(self.sp_proxies.keys()) == 0:
                return False

            if self._auto_change_proxy:
                oldproxy = memo.get('proxy')
                if oldproxy in self.sp_proxies:
                    self.sp_proxies[oldproxy] += 1
                prs = self.sp_proxies.keys()

                for i in range(len(prs)):
                    self._cur_proxy_index = (self._cur_proxy_index + 1) % len(prs)
                    selproxy = prs[self._cur_proxy_index]
                    if self.sp_proxies.get(selproxy, 0) <= 10:
                        memo['proxy'] = selproxy
                        self._set_proxy(kwargs, selproxy)
                        return True

            elif self._cur_proxy_index < 0:
                # don't auto change proxy, and the index < 0, no proxy is used.
                # but don't report an error.
                return True
            else:
                prs = self.sp_proxies.keys()
                selproxy = prs[self._cur_proxy_index % len(prs)]
                self._set_proxy(kwargs, selproxy)
                return True

        return False

    def _new_request_worker(self):
        return CurlReq(None)

    def _do_requests(self, url, **kwargs):
        curl = getattr(self._curltls, 'curl', None)
        if curl is None:
            curl = self._new_request_worker()
            setattr(self._curltls, 'curl', curl)
        return curl.doreq(url, **kwargs)

    def req_content_check(self, url, resp):
        return True

    def _on_req_success(self, kwargs, memo, response):
        if isinstance(self.sp_proxies, dict) and len(self.sp_proxies.keys()) > 0:
            oldproxy = memo.get('proxy')
            if oldproxy is not None and oldproxy in self.sp_proxies:
                self.sp_proxies[oldproxy] = 0

    def request_url(self, url, **kwargs):
        headers1 = copy.deepcopy(self.default_headers)
        headers1.update({'User-Agent': self._user_agent})
        if 'headers' in kwargs:
            headers1.update(kwargs['headers'])

        kwargs['headers'] = headers1
        kwargs.setdefault('timeout', 30)
        memo = {}
        setattr(self._curltls, 'is_proxy_error', False)

        if len(self.sp_proxies) > 0:
            if not self._replace_proxy(kwargs, memo):
                raise RuntimeError('no proxy')


        i = 0
        while i < 3:
            i += 1
            try:
                response = self._do_requests(url, **kwargs)
                if self.req_content_check(url, response):
                    self._on_req_success(kwargs, memo, response)
                    return response
            except (KeyboardInterrupt, SystemExit):
                raise
            except ProxyError as e:
                setattr(self._curltls, 'is_proxy_error', True)
                print "proxy failed %s" % url, e.reason

                if i >= 2and self._auto_change_proxy and self._replace_proxy(kwargs, memo):
                    i = 0
                    print "retry using proxy ", kwargs.get('proxy','')
            except DNSError as e:
                Log.warning("dns for %s error!" % e.hostname)
                time.sleep(3)
                i -= 1
            except Exception as e:
                if not self.on_other_http_exception(e):
                    hpr = kwargs.get('proxy', {}).get('http', '')
                    Log.error('FAIL : req %s proxy=%s, err=' % (url, hpr), str(type(e)), str(e))
                    traceback.print_exc()

            time.sleep(1)

        return None

    def on_other_http_exception(self, exception):
        """
        other exception handler
        :return True if exception is handled,False otherwise
        """
        return False


class SpeedControlRequests(BasicRequests):
    def __init__(self):
        BasicRequests.__init__(self)

    def with_sleep_requests(self, url, sleep=0, **kwargs):
        time.sleep(sleep)
        return self.request_url(url, **kwargs)


class SessionRequests(BasicRequests):
    def __init__(self):
        BasicRequests.__init__(self)
        self._curlshare=pycurl.CurlShare()
        self._curlshare.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_DNS)
        self._curlshare.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_COOKIE)

    def _new_request_worker(self):
        return CurlReq(self._curlshare)

    def _do_requests(self, url, **kwargs):
        rv = BasicRequests._do_requests(self, url, **kwargs)

        if rv is not None:
            curlckjar = getattr(self._curltls, "cookies", None)
            if curlckjar is None:
                curlckjar = CurlCookieJar()

            curlckjar.add_list(rv.cookies)
            setattr(self._curltls, 'cookies', curlckjar)

        return rv

    def reset_session(self):
        cs = pycurl.CurlShare()
        cs.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_DNS)
        cs.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_COOKIE)
        self._curlshare = cs
        curl = self._new_request_worker()
        setattr(self._curltls, 'curl', curl)

    def get_cookie(self, cookiename, defaultv='', domain='', path='/'):
        curlckjar = getattr(self._curltls, 'cookies', None)
        if curlckjar is None:
            raise RuntimeError("NO COOKIE IN curltls")

        ck = curlckjar.get_cookie(domain, path, cookiename)
        if ck is None:
            return defaultv
        else:
            return ck.value

    def _boolv_(self, v):
        if not v:
            return "FALSE"
        return "TRUE"

    def add_cookie(self, domain, name, value, domain_specified="?", path="/", secure="FALSE", expires=0):
        if domain_specified == '?':
            if domain[0:1] == '.':
                domain_specified = "TRUE"
            else:
                domain_specified = "FALSE"
        domain_specified = self._boolv_(domain_specified)
        secure = self._boolv_(secure)
        if expires is None:
            expires = 0

        curl = getattr(self._curltls, 'curl', None)
        if curl is None:
            curl = self._new_request_worker()
            setattr(self._curltls, 'curl', curl)

        ck_ = [domain, domain_specified, path, secure, str(expires), name, value]
        curl.curl.setopt(pycurl.COOKIELIST, "\t".join(ck_))

        curlckjar = getattr(self._curltls, 'cookies', None)
        if curlckjar is not None:
            curlckjar._add_cookie(domain, name, value, domain_specified, path, secure, expires)

    def add_cookie_line(self, domain, cookie_line):
        curl = getattr(self._curltls, 'curl', None)
        if curl is None:
            curl = self._new_request_worker()
            setattr(self._curltls, 'curl', curl)
        if re.search(r';\s*domain\s*=', cookie_line, re.I):
            # ignore the domain argument.
            pass
        else:
            assert isinstance(domain, str) or isinstance(domain, unicode)
            domain = re.sub(r'.*?@', '', domain)
            domain = re.sub(r':.*', '', domain)
            assert domain != ''
            if re.search(r';', cookie_line):
                cookie_line = re.sub(';', '; domain=%s;' % domain, cookie_line)
            else:
                cookie_line = cookie_line + ('; domain=%s;' % domain)

        if cookie_line[0:11] == "Set-Cookie:":
            curl.curl.setopt(pycurl.COOKIELIST, cookie_line)
        else:
            curl.curl.setopt(pycurl.COOKIELIST, "Set-Cookie: " + cookie_line)

        curlckjar = CurlCookieJar()
        setattr(self._curltls, 'cookies', curlckjar)
        curlckjar.add_list(curl.curl.getinfo(pycurl.INFO_COOKIELIST))
















