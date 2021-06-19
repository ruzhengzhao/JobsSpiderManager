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


def _save_as_excel(informations, header, path):
    # list(dict)格式数据保存为excel
    excel = xlwt.Workbook()
    # 设置单元格
    sheet1 = excel.add_sheet('Job', cell_overwrite_ok=True)
    sheet1.write(0, 0, '序号')
    sheet1.write(0, 1, '职位')
    sheet1.write(0, 2, '公司名称')
    sheet1.write(0, 3, '薪酬')
    sheet1.write(0, 4, '发布时间')
    sheet1.write(0, 5, '公司地点')
    sheet1.write(0, 6, '经验要求')
    sheet1.write(0, 7, '学历要求')
    sheet1.write(0, 8, '需求人数')
    sheet1.write(0, 9, '任职要求')

    for i, information in enumerate(informations):
        try:
            job_url = information['job_href']
            job_html = _get_51job_job_html(job_url, header)
            job_require = _get_51job_requirements(job_html)
            print(job_require)

            sheet1.write(i+1, 0, i+1)  # 序号
            sheet1.write(i+1, 1, information['job_name'])  # 职位
            sheet1.write(i+1, 2, information['company_name'])  # 公司名称
            sheet1.write(i+1, 3, information['providesalary_text'])   #薪酬
            sheet1.write(i+1, 4, information['updatedate'])  # 发布时间
            sheet1.write(i+1, 5, information['attribute_text'][0])  # 公司地点
            sheet1.write(i+1, 6, information['attribute_text'][1])  # 经验要求
            sheet1.write(i+1, 7, information['attribute_text'][2])  # 学历要求
            sheet1.write(i+1, 8, _get_recruiting_numbers(information['attribute_text']))  # 需求人数
            sheet1.write(i+1, 9, job_require)  # 任职要求

        except Exception as e:
            print(job_url)
    excel.save(path)


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
