#!/usr/bin/env python
#coding:utf-8
import apicn as DnsBase
import re

class Dnspod(object):
    """
    这层没有try-except机制，如果dnspod返回出错，会直接panic到上层去
    所以上层需要有try机制，以封装异常,不能让异常影响manager层。
    """
    
    @classmethod
    def DomainInfo(cls, domain_name):
        """Get Domain Info, not record!
        有无前缀都可以，最后获取的是domain的一个基本情况
        """
        suffix = cls.GetDomainSuffix(domain_name)
        param = {}
        param["domain"] = suffix
        ret = DnsBase.DomainInfo(**param)()

        return ret

    @classmethod
    def DomainId(cls, domain_name):
        """Get Domain Id, by domain_name!
        有无前缀都可以，最后获取的是domain的id, 字符串哦
        """
        info = cls.DomainInfo(domain_name)
        did = info["domain"]["id"]
        return did

    @classmethod
    def DomainGrade(cls, domain_name):
        """获取domain的等级，也就是dnspod的套餐等级，用来获取等级相关信息
        """
        info = cls.DomainInfo(domain_name)
        dgrade = info["domain"]["grade"]
        return dgrade

    @classmethod
    def RecordLine(cls, domain_name):
        """Get Domain Line!
        """
        suffix = cls.GetDomainSuffix(domain_name)
        param = {}
        param["domain"] = suffix
        grade = cls.DomainGrade(domain_name)
        ret = DnsBase.RecordLine(grade, **param)()
        lines = ret["lines"]
        return lines

    @classmethod
    def RecordCreate(cls, domain_name, record_type, record_line, value, ttl, status):
        """Add a Record, domain表示prefix + suffix
        """
        did = cls.DomainId(domain_name)
        sub_domain, domain = cls.SeparateDomain(domain_name)
        params = {}
        params["domain_id"] = did
        params["domain"] = domain
        ret = DnsBase.RecordCreate(sub_domain, record_type, record_line, value, ttl, status, **params)()
        if ret:
            return ret["record"]["id"]

    @classmethod
    def RecordList(cls, domain_name):
        did = cls.DomainId(domain_name)
        sub_domain, domain = cls.SeparateDomain(domain_name)
        params = {}
        params["sub_domain"] = sub_domain
        params["domain"] = domain
        ret = DnsBase.RecordList(did, **params)()

        if ret:
            return ret["records"]

    @classmethod
    def RecordModify(cls, domain_name, record_id, record_type, record_line, value, ttl, status):
        """修改记录， 可以连status一起修改，Yizero赞一个
        """
        did = cls.DomainId(domain_name)
        sub_domain, domain = cls.SeparateDomain(domain_name)
        ret = DnsBase.RecordModify(record_id, did, sub_domain, domain, record_type, record_line, value, ttl, status)()
        if ret:
            return ret

    @classmethod
    def RecordRemark(cls, domain_name, record_id, remark):
        """修改记录备注
        """
        did = cls.DomainId(domain_name)
        domain = cls.GetDomainSuffix(domain_name)
        params = dict(
            domain = domain,
            domain_id = did,
            record_id = record_id,
            remark = remark
        )
        ret = DnsBase.RecordRemark(**params)()
        if ret:
            return ret

    @classmethod
    def RecordStatus(cls, domain_name, record_id, status):
        """修改记录状态
        """
        did = cls.DomainId(domain_name)
        domain = cls.GetDomainSuffix(domain_name)
        params = dict(
            domain = domain,
            domain_id = did,
            record_id = record_id,
            status = status
        )
        ret = DnsBase.RecordStatus(**params)()
        if ret:
            return ret

    @classmethod
    def RecordRemove(cls, domain_name, record_id):
        """记录删除
        """
        did = cls.DomainId(domain_name)
        domain = cls.GetDomainSuffix(domain_name)
        params = dict(
            domain = domain,
            domain_id = did
        )
        ret = DnsBase.RecordRemove(record_id, **params)()
        if ret:
            return ret

    @classmethod
    def SeparateDomain(cls, domain_name):
        """切分域名
        需兼容各种前缀、无前缀、二级后缀、三级后缀情况
        """
        bk_domain_list = ["com.cn"]
        #顶级域名为两级的时候（xiaomi.com, wali.com）
        name_prefix_reg = re.compile("(?P<prefix>^[@a-zA-Z0-9-_.*]+)\.(?P<suffix>[a-zA-Z0-9-]+\.[a-zA-Z]+$)")
        #顶级域名为三级的时候 (mi-ae.com.cn)
        name_prefix_reg_bk = re.compile("(?P<prefix>^[@a-zA-Z0-9-_.*]+)\.(?P<suffix>[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.[a-zA-Z]+$)")

        res = name_prefix_reg.match(domain_name)
        if not res:
            domain_name = "@." + domain_name
            res = name_prefix_reg.match(domain_name)
        if res:
            suffix = res.groupdict()["suffix"]
            prefix = res.groupdict()["prefix"]
            #如果domain在列表中，说明需要用另一个正则来匹配
            if suffix in bk_domain_list:
                res = name_prefix_reg_bk.match(domain_name)
                if not res:
                    res = name_prefix_reg_bk.match("@." + domain_name)
                if res:
                    suffix = res.groupdict()["suffix"]
                    prefix = res.groupdict()["prefix"]
        else:
            raise Exception(u"无法切分域名")

        return prefix, suffix

    @classmethod
    def GetDomainPrefix(cls, domain_name):
        pre, suff = cls.SeparateDomain(domain_name)
        return pre

    @classmethod
    def GetDomainSuffix(cls, domain_name):
        pre, suff = cls.SeparateDomain(domain_name)
        return suff

if __name__ == "__main__":
    try:
        #x = Dnspod.RecordCreate("haha.luoxiao.com", "CNAME", u"默认", "baidu.com", "600", "enable")
        #x = Dnspod.RecordList("haha.luoxiao.com")
        x = Dnspod.RecordStatus("haha.luoxiao.com", "108275555", "disable")
        #for y in x:
        print x
    except Exception,e:
        print e.message
