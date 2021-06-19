from django.db import models


class JobInfo(models.Model):

    id = models.AutoField(primary_key=True)
    job_id = models.CharField(max_length=100, unique=True)
    job_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    provide_salary = models.CharField(max_length=100)
    update_date = models.CharField(max_length=100)
    company_location = models.CharField(max_length=100)
    experience_requirement = models.CharField(max_length=100)
    academic_requirements = models.CharField(max_length=100)
    demand_num = models.CharField(max_length=100)
    job_requirements = models.CharField(max_length=100)

    def __str__(self):
        return self.job_name