# -*- coding:utf-8 -*-

import urllib.request
import xlwt
import re
import urllib.parse
import json


class JobInformation:
    def __init__(self):
        self.job_id = ""
        self.job_name = ""
        self.company_name = ""
        self.provide_salary = ""
        self.update_date = ""
        self.company_location = ""
        self.experience_requirement = ""
        self.academic_requirements = ""
        self.demand_num = ""
        self.job_requirements = ""

def _get_51job_page_html(page, header):
    # 获取html
    ur1 = str(page)+'.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare='
    ur2 = 'https://search.51job.com/list/030000,000000,5800,29%252c20,3,99,+,2,'
    url = ur2+ur1
    # print(url)
    request = urllib.request.Request(url, headers=header)
    response = urllib.request.urlopen(request)
    html = response.read().decode('gbk')
    # print(html)# 读取源代码并转为unicode
    return html


def _analysis_51job_information(html):
    # 解析html保存为list(dict)格式
    jobs = []
    reg = '(?<=window.__SEARCH_RESULT__ = ).*?(?=</script>)'
    json_infos = re.findall(reg, html)
    # print("正则匹配成功数：{0}".format(len(json_infos)))
    # print(json_infos)
    for json_info in json_infos:
        json_data = json.loads(json_info)
        if 'engine_search_result' in json_data:
            # print("待解析岗位数：{0}".format(len(json_data['engine_search_result'])))
            for raw_info in json_data['engine_search_result']:
                info = JobInformation()
                info.job_id = raw_info.get("jobid", "")
                info.job_name = raw_info.get("job_name", "")
                info.company_name = raw_info.get("company_name", "")
                info.provide_salary = raw_info.get("providesalary_text", "")
                info.update_date = raw_info.get("updatedate", "")
                attribute_text = raw_info.get("attribute_text", [])
                if len(attribute_text) > 0:
                    info.company_location = attribute_text[0]
                if len(attribute_text) > 1:
                    info.experience_requirement = attribute_text[1]
                if len(attribute_text) > 2:
                    info.academic_requirements = attribute_text[2]
                info.demand_num = _get_recruiting_numbers(raw_info.get("attribute_text", ["", "", ""]))
                info.job_requirements = ""
                jobs.append(info)
    # print("解析成功岗位数：{0}".format(len(jobs)))
    return jobs

def _get_recruiting_numbers(attribute_list):
    # 招工数解析
    reg = r'(?<=招).*?(?=人)'
    for attribute in attribute_list:
        matchObj = re.search(reg, attribute)
        if matchObj:
            return matchObj.group(0)
    return ""


def _get_51job_job_html(url, header):
    request = urllib.request.Request(url, headers=header)
    response = urllib.request.urlopen(request)
    html = response.read().decode('gbk')
    return html


def _get_51job_requirements(html):
    job_requirements = re.findall(re.compile(
        r' <div class="bmsg job_msg inbox">.*?<p>(.*?)<div class="mt10">',
        re.S), html)
    return job_requirements


def _get_zhaopin_page_html(page, header):
    # 获取html
    ur1 = str(page) + '&dt=4&ind=600000000&jt=21000100000000'
    ur2 = 'https://xiaoyuan.zhaopin.com/search/jn=2&cts=548&pg='
    url = ur2 + ur1
    #print(url)
    request = urllib.request.Request(url, headers=header)
    response = urllib.request.urlopen(request)
    html = response.read().decode('utf-8')
    # print(html)# 读取源代码并转为unicode
    return html


def _analysis_zhaopin_information(html):
    # 解析html保存为list(dict)格式
    jobs = []
    reg = '(?<=__INITIAL_STATE__=).*?(?=</script>)'
    json_infos = re.findall(reg, html)
    # print("正则匹配成功数：{0}".format(len(json_infos)))
    # print(json_infos)
    for json_info in json_infos:
        json_data = json.loads(json_info)
        if 'souresult' in json_data:
            # print("待解析岗位数：{0}".format(len(json_data['engine_search_result'])))
            for raw_info in json_data['souresult']['Items']:
                info = JobInformation()
                info.job_id = raw_info.get("JobPositionNumber", "")
                info.job_name = raw_info.get("JobTitle", "")
                info.company_name = raw_info.get("CompanyName", "")
                info.provide_salary = raw_info.get("MaxSalary", "")
                info.update_date = raw_info.get("DateCreated", "")
                info.demand_num = raw_info.get("RecruitCount", "")
                info.company_location = raw_info.get("CityName", "")
                jobs.append(info)
    # print("解析成功岗位数：{0}".format(len(jobs)))
    return jobs


def crawling_51bob_infomation(page_num):
    # 模拟浏览器
    header = {
        'Host': 'search.51job.com',
        'Referer': 'https://search.51job.com/list/030000,000000,5800,29%252c20,3,99,+,2,1.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=01%252c02%252c03&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare=',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    information = []
    for i in range(1, page_num+1):
        page_html = _get_51job_page_html(i, header)
        # print(page_html)
        page_information = _analysis_51job_information(page_html)
        information += page_information
    return information


def crawling_zhaopin_infomation(page_num):
    # 模拟浏览器
    header = {
        'authority': 'xiaoyuan.zhaopin.com',
        'path': '/search/jn=2&cts=548&pg=1&dt=4&ind=600000000&jt=21000100000000',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    information = []
    for i in range(1, page_num+1):
        page_html = _get_zhaopin_page_html(i, header)
        # print(page_html)
        page_information = _analysis_zhaopin_information(page_html)
        information += page_information
    return information