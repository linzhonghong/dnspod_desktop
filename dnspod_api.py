#-*- coding:utf-8 -*-
__author__ = 'linzhonghong'

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import urllib2,cookielib,urllib
import re
import traceback
import time

class dnspod_api(object):

    def __init__(self,user="",passwd="",domain="yourdomain.com"):
        self.cookies = cookielib.LWPCookieJar()
        cookie_support = urllib2.HTTPCookieProcessor(self.cookies)
        opnner = urllib2.build_opener(cookie_support,urllib2.HTTPHandler,urllib2.HTTPSHandler)
        urllib2.install_opener(opnner)
        self.user = user
        self.passwd = passwd
        self.headers = {}
        self.headers["User-Agent"]='Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)'
        self.common_parm = self.__common_parm()
        self.domian_id = self.get_domain_info(domian=domain)

    #公共参数
    def __common_parm(self):
        common_parm = {}
        common_parm['login_email'] = self.user
        common_parm['login_password'] = self.passwd
        common_parm['format'] = 'json'
        common_parm['lang'] = 'cn'
        common_parm['error_on_empty'] = 'no'
        return common_parm

    #创建参数
    def __create_parm(self,parm=None):
        parm.update(self.common_parm)
        return urllib.urlencode(parm)

    #发送请求并返回结果
    def __post_data(self,parm,api_url=""):
        request = urllib2.Request(api_url,parm,self.headers)
        response = urllib2.urlopen(request).read()
        ret = json.JSONDecoder().decode(response)
        if ret.has_key('status'):
            if ret['status']['code'] =="1":
                return ("ok",ret)
            else:
                return (ret['status']['message'],ret)
        else:
            return (u'未知错误',{})

    #获取指定域名ID
    def get_domain_info(self,domian=""):
        message,result = self.__post_data(self.__create_parm(parm={'domain':domian}),api_url='https://dnsapi.cn/Domain.Info')
        return result['domain']['id']

    #获记录列表
    def record_list(self,sub_domain="",type="record_id",offset=""):
        parm = {}
        parm['domain_id'] = self.domian_id
        parm['sub_domain'] = sub_domain
        parm['offset'] = offset
        message,result = self.__post_data(self.__create_parm(parm=parm),api_url='https://dnsapi.cn/Record.List')
        if type == "total":
            return message,result['records']
        if type == "record_id":
            record_id_list = []
            for record in result['records']:
                record_id_list.append(record['id'])
            return message,record_id_list
        if type == "record":
            record_list = []
            for record in result['records']:
                record_list.append(dict(id=record['id'],enabled=record['enabled'],name=record['name'],type=record['type'],
                                        value=record['value'],ttl=record['ttl'],line=record['line'],))
            return message,record_list

    #获取记录信息
    def record_info(self,record_id):
        parm = {}
        parm['domain_id'] = self.domian_id
        parm['record_id'] = record_id
        message,result = self.__post_data(self.__create_parm(parm=parm),api_url='https://dnsapi.cn/Record.Info')
        return message,result

    #创建记录
    def record_create(self,sub_domain="",record_type="",record_line="",value=""):
        result_message='传入参数错误'
        api_url='https://dnsapi.cn/Record.Create'
        parm = {}
        parm['domain_id'] = self.domian_id
        parm['sub_domain'] = sub_domain
        parm['record_type'] = record_type
        parm['record_line'] = record_line
        parm['value'] = value
        if record_type == "CNAME":
            if not value.endswith('.'):
                parm['value'] = "%s."%value
        message,result = self.__post_data(self.__create_parm(parm=parm),api_url=api_url)
        if message == 'ok' and result['status']['code'] == '1':
            return (1, {'rec_id': result['record']['id'], 'status':result['record']['status']})
        else:
            return (0, {})

    #修改记录
    def record_modify(self, record_id, sub_domain="",record_type="",record_line="",value=""):
        api_url='https://dnsapi.cn/Record.Modify'
        parm = {}
        parm['domain_id'] = self.domian_id
        parm['record_id'] = record_id
        parm['sub_domain'] = sub_domain
        parm['record_type'] = record_type
        parm['record_line'] = record_line
        parm['value'] = value
        if not record_id:
            return (0, '参数错误')
        message,result = self.__post_data(self.__create_parm(parm=parm),api_url=api_url)
        if message == 'ok' and result['status']['code'] == '1':
            return (1, 'ok')
        else:
            return (0, '接口请求失败:%s'%result['status']['message'])

    #设置状态
    def record_status(self,record_id,status="",rec_name=''):
        parm = {}
        parm['domain_id'] = self.domian_id
        parm['record_id'] = record_id
        parm['status'] = status
        if status != "enable" and status != "disable":
            return (0, '参数错误')
        message,record_info = self.record_info(record_id)
        if message == 'ok':
            message,result = self.__post_data(self.__create_parm(parm=parm),api_url='https://dnsapi.cn/Record.Status')
            if message == 'ok' and result['status']['code'] == '1':
                return (1, 'ok')
            else:
                return (0, '接口请求失败')
        else:
            return (0, '%s 不存在' % record_id)

    #删除记录
    def record_delete(self,record_id='',rec_name=''):
        if not all([record_id]):
            return 0
        api_url='https://dnsapi.cn/Record.Remove'
        parm = {}
        parm['domain_id'] = self.domian_id
        parm['record_id'] = record_id
        message,result = self.__post_data(self.__create_parm(parm=parm),api_url=api_url)
        if message == 'ok' and result['status']['code'] == '1':
            return 1
        else:
            return 0

if __name__ == '__main__':
    pass