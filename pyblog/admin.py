from django.contrib import admin
from django.urls import reverse
from pyblog.models import *
from django.utils.html import format_html
from django.utils.http import urlencode

# Register your models here.
class BookJob(admin.ModelAdmin):
	list_display= [field.name for field in Job._meta.fields]+['add_link',]
	def add_link(self, obj):
		url = (
			"http://127.0.0.1:8000/"
            + "blogs/"
            + str(obj.id)+"/"
		)
		return format_html('<a href="{}">Fetch</a>', url)
	add_link.short_description = "Job"
	

class BookBlog(admin.ModelAdmin):
	list_display= [field.name for field in Blog._meta.fields]
class BookAuthor(admin.ModelAdmin):
	list_display= [field.name for field in Author._meta.fields]
class BookLog(admin.ModelAdmin):
	list_display= [field.name for field in Log._meta.fields]
class BookStats(admin.ModelAdmin):
	list_display= [field.name for field in Stats._meta.fields]
class BookLink(admin.ModelAdmin):
	list_display= [field.name for field in Link._meta.fields]	
	
admin.site.register(Job,BookJob)
admin.site.register(Blog,BookBlog)
admin.site.register(Log,BookLog)
admin.site.register(Stats,BookStats)
admin.site.register(Link,BookLink)
admin.site.register(Author,BookAuthor)
