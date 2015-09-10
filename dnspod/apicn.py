#!/usr/bin/env python
#-*- coding:utf-8 -*-

import httplib, urllib
import requests as Requests
try: import json
except: import simplejson as json
import socket
import os
import re
import pyg2fa as OtpLib

DNS_ACCOUNTS = {}


class ApiCn:

    def __init__(self, **kw):
        self.base_url = "https://dnsapi.cn"
        
        self.params = {}
        self.params.update(kw)
        self.path = None
    
    def request(self, **kw):
        self.params.update(kw)
        self.params = self._add_account_msg(kw=self.params)

        if not self.path:
            """Class UserInfo will auto request path /User.Info."""
            name = re.sub(r'([A-Z])', r'.\1', self.__class__.__name__)
            self.path = "/" + name[1:]
        
        headers = self._get_headers()
        r_url = self.base_url + self.path
        r = Requests.post(r_url , self.params, headers = headers, verify=False)
        if r.status_code != 200:
            raise Exception(u"[%s]调用dnspod接口异常，返回值：%d" % (self.path, r.status_code))
        ret = r.json()
        if ret.get("status", {}).get("code") == "1":
            return ret
        else:
            msg = u"[%s][err_code:%s]%s" % (self.path, ret["status"]["code"], ret["status"]["message"])
            raise Exception(msg)


    def _get_headers(self):
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json", "User-Agent": "dnspod-python/0.01 (im@chuangbo.li; DNSPod.CN API v2.8)"}
        return headers

    def _add_account_msg(self, kw={}):
        #需要一个DNS_ACCOUNTS
        if "domain" not in kw:
            raise Exception(u"[BUG]'domain' not in function, cannot get account msg")
        else:
            domain = kw["domain"]
        if "default" not in DNS_ACCOUNTS and domain not in DNS_ACCOUNTS:
            return kw
        dnskey = DNS_ACCOUNTS["default"]
        if domain and domain in DNS_ACCOUNTS:
            dnskey = DNS_ACCOUNTS[domain]
        account, passwd, seed = dnskey.decode("base64").split(" ")
        code = OtpLib.generate_opt_token(seed, 0)
        params = {"login_code":code, "login_remember":"no", "login_email":account, "login_password": passwd, "format":"json", "lang":"cn"}
        params.update(kw)

        return params

    __call__ = request
    
class InfoVersion(ApiCn):
    pass

class UserDetail(ApiCn):
    pass

class UserInfo(ApiCn):
    pass

class UserLog(ApiCn):
    pass

class DomainCreate(ApiCn):
    def __init__(self, domain, **kw):
        kw.update(dict(domain=domain))
        ApiCn.__init__(self, **kw)

class DomainId(ApiCn):
    def __init__(self, domain, **kw):
        kw.update(dict(domain=domain))
        ApiCn.__init__(self, **kw)

class DomainInfo(ApiCn):
    def __init__(self, **kw):
        ApiCn.__init__(self, **kw)

class DomainList(ApiCn):
    pass

class _DomainApiBase(ApiCn):
    def __init__(self, domain_id, **kw):
        kw.update(dict(domain_id=domain_id))
        ApiCn.__init__(self, **kw)

class DomainRemove(_DomainApiBase):
    pass
        
class DomainStatus(_DomainApiBase):
    def __init__(self, status, **kw):
        kw.update(dict(status=status))
        _DomainApiBase.__init__(self, **kw)
        

class DomainLog(_DomainApiBase):
    pass

class RecordType(ApiCn):
    def __init__(self, domain_grade, **kw):
        kw.update(dict(domain_grade=domain_grade))
        ApiCn.__init__(self, **kw)
        
class RecordLine(ApiCn):
    def __init__(self, domain_grade, **kw):
        kw.update(dict(domain_grade=domain_grade))
        ApiCn.__init__(self, **kw)

class RecordCreate(_DomainApiBase):
    def __init__(self, sub_domain, record_type, record_line, value, ttl, status="enable", mx=None, **kw):
        kw.update(dict(
            sub_domain=sub_domain,
            record_type=record_type,
            record_line=record_line,
            status = status,
            value=value,
            ttl=ttl,
        ))
        if mx:
            kw.update(dict(mx=mx))
        _DomainApiBase.__init__(self, **kw)

class RecordModify(_DomainApiBase):
    def __init__(self, record_id, domain_id, sub_domain, domain, record_type, record_line, value, ttl, status="enable", mx=None, **kw):
        kw.update(dict(
            record_id=record_id,
            sub_domain = sub_domain,
            domain = domain,
            record_type = record_type,
            record_line = record_line,
            value = value,
            ttl = ttl,
            status = status,
        ))
        if mx:
            kw.update(dict(mx=mx))
        _DomainApiBase.__init__(self, domain_id, **kw)
 
class RecordRemark(ApiCn):
    pass

class RecordList(_DomainApiBase):
    pass

class _RecordBase(_DomainApiBase):
    def __init__(self, record_id, **kw):
        kw.update(dict(record_id=record_id))
        _DomainApiBase.__init__(self, **kw)

class RecordRemove(_RecordBase):
    pass

class RecordDdns(_DomainApiBase):
    def __init__(self, record_id, sub_domain, record_line, **kw):
        kw.update(dict(
            record_id=record_id,
            sub_domain=sub_domain,
            record_type=record_type,
            record_line=record_line,
        ))
        _DomainApiBase.__init__(self, **kw)

class RecordStatus(ApiCn):
    pass

class RecordInfo(_RecordBase):
    pass


if __name__ == "__main__":
    pass
