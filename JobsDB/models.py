from django.db import models


class JobInfo(models.Model):

    id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    job_id = models.CharField(max_length=100, unique=True)
    job_name = models.CharField(max_length=100, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    provide_salary = models.CharField(max_length=100, null=True, blank=True)
    update_date = models.CharField(max_length=100, null=True, blank=True)
    company_location = models.CharField(max_length=100, null=True, blank=True)
    experience_requirement = models.CharField(max_length=100, null=True, blank=True)
    academic_requirements = models.CharField(max_length=100, null=True, blank=True)
    demand_num = models.CharField(max_length=100, null=True, blank=True)
    job_requirements = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.job_name