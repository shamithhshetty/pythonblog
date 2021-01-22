from django.shortcuts import render
import datetime
from django.http import HttpResponse
from .tasks import *
from .task import *
from django.http import HttpResponseRedirect

# Create your views here.
def blogs(request,job_id):
    job_obj = Job.objects.get(id=job_id)
    stats_obj = Stats.objects.create(job = job_obj, status = "Starting....", start_time = datetime.datetime.now())
    log_obj = Log.objects.create(stat = stats_obj, message = "Stating..", time = datetime.datetime.now() )
    scrape.delay(job_id,stats_obj.id)
    return HttpResponseRedirect('/admin/pyblog/job')

def fetch(request,job_id):
    job_obj = Job.objects.get(id=job_id)
    stats_obj = Stats.objects.create(job = job_obj, status = "Starting....", start_time = datetime.datetime.now())
    log_obj = Log.objects.create(stat = stats_obj, message = "Stating..", time = datetime.datetime.now() )
    extractor.delay(job_id,stats_obj.id)
    return HttpResponseRedirect('/admin/pyblog/job')
