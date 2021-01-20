from django.shortcuts import render
from django.http import HttpResponse
from .tasks import *
# Create your views here.
def blogs(request,job_id):
	scrape.delay(job_id)
	return HttpResponse(str(job_id))
