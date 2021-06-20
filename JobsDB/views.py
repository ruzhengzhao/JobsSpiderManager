import random
import math
import xlwt
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from pyecharts.charts import Page, Bar
from pyecharts import options as opts

from .models import JobInfo
from Spider.spider import crawling_51bob_infomation, crawling_zhaopin_infomation


def index(request):
    jobs_list = JobInfo.objects.all()
    context = {
        'jobs_num': len(jobs_list),
        'jobs_list': jobs_list.order_by('?')[:10],
    }
    return render(request, 'JobsDB/index.html', context)


def delete(request):
    try:
        del_job_id = request.POST['del_job_id']
        JobInfo.objects.filter(job_id=del_job_id).delete()
    except (KeyError, JobInfo.DoesNotExist):
        pass
    return HttpResponseRedirect(reverse('JobsDB:overview'))


def delete_all(request):
    try:
        if request.POST['del_all'] == 'True':
            JobInfo.objects.all().delete()
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('JobsDB:overview'))


def collect(request):
    try:
        page_num = int(request.POST['page_num'])
        if page_num < 1:
            raise ValueError
        job_web = request.POST['job_web']
    except KeyError:
        return render(request, "JobsDB/collect.html")
    except ValueError:
        context = {
            "error_message": "爬取页数输入错误",
        }
        return render(request, "JobsDB/collect.html", context)
    else:
        if job_web == '51job':
            new_list = crawling_51bob_infomation(page_num)
            source = '前程无忧'
        elif job_web == 'zhaopin':
            new_list = crawling_zhaopin_infomation(page_num)
            source = '智联招聘'
        else:
            new_list = []
            source = '未知'

        new_size = len(new_list)
        update_size = 0
        create_size = 0
        error_size = 0
        new_info = []
        for information in new_list:
            try:
                info = JobInfo.objects.get(job_id=information.job_id)
                update_size += 1
            except JobInfo.DoesNotExist:
                info = JobInfo()
                create_size += 1
            except:
                error_size += 1
                continue

            info.source = source
            info.job_id = information.job_id
            info.job_name = information.job_name
            info.company_name = information.company_name
            info.provide_salary = information.provide_salary
            info.update_date = information.update_date
            info.company_location = information.company_location
            info.experience_requirement = information.experience_requirement
            info.academic_requirements = information.academic_requirements
            info.demand_num = information.demand_num
            info.job_requirements = information.job_requirements
            info.save()
            new_info.append(info)
        random.shuffle(new_info)
        context = {
            'jobs_num': len(JobInfo.objects.all()),
            'new_size': new_size,
            'update_size': update_size,
            'create_size': create_size,
            'error_size': error_size,
            'jobs_list': new_info[:10],
        }
        return render(request, 'JobsDB/collect.html', context)


def overview(request):
    jobs_list = JobInfo.objects.all()
    context = {
        'jobs_num': len(jobs_list),
        'jobs_list': jobs_list,
    }
    return render(request, 'JobsDB/overview.html', context)


def download(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment;filename="jobs.xls"'
    excel = xlwt.Workbook(encoding='utf-8')
    sheet = excel.add_sheet('Job')

    sheet.write(0, 0, 'ID')
    sheet.write(0, 1, '职位')
    sheet.write(0, 2, '公司名称')
    sheet.write(0, 3, '薪酬')
    sheet.write(0, 4, '发布时间')
    sheet.write(0, 5, '公司地点')
    sheet.write(0, 6, '经验要求')
    sheet.write(0, 7, '学历要求')
    sheet.write(0, 8, '需求人数')
    sheet.write(0, 9, '任职要求')
    sheet.write(0, 10, '数据来源')

    for i, info in enumerate(JobInfo.objects.all()):
        sheet.write(i + 1, 0, info.job_id)  # 序号
        sheet.write(i + 1, 1, info.job_name)  # 职位
        sheet.write(i + 1, 2, info.company_name)  # 公司名称
        sheet.write(i + 1, 3, info.provide_salary)  # 薪酬
        sheet.write(i + 1, 4, info.update_date)  # 发布时间
        sheet.write(i + 1, 5, info.company_location)  # 公司地点
        sheet.write(i + 1, 6, info.experience_requirement)  # 经验要求
        sheet.write(i + 1, 7, info.academic_requirements)  # 学历要求
        sheet.write(i + 1, 8, info.demand_num)  # 需求人数
        sheet.write(i + 1, 9, info.job_requirements)  # 任职要求
        sheet.write(i + 1, 10, info.source)  # 数据来源
    excel.save(response)
    return response


def analysis(request):
    salary_list = []
    for info in JobInfo.objects.all():
        try:
            salary_list.append(int(info.provide_salary))
        except ValueError:
            continue
    interval_boundary = [0, 5000, 8000, 17000, 30000]
    interval_name_list = []
    interval_count = []
    for i in range(len(interval_boundary)-1):
        interval_name_list.append("[{0}-{1}]".format(interval_boundary[i], interval_boundary[i+1]))
        interval_count.append(len([s for s in salary_list if interval_boundary[i + 1] > s >= interval_boundary[i]]))
    page = Page()
    chart = (
        Bar()
            .add_xaxis(interval_name_list)
            .add_yaxis("收入区间", interval_count)
            .set_global_opts(title_opts=opts.TitleOpts(title="收入分布"))
    )
    page.add(chart)
    return HttpResponse(page.render_embed())
