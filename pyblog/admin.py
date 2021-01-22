from django.contrib import admin
from django.urls import reverse
from pyblog.models import *
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse
from django.utils.html import format_html
from .tasks import *

# Register your models here.
class BookJob(admin.ModelAdmin):
	list_display= [field.name for field in Job._meta.fields]+['add_link',]
	search_fields = ('id',)
	def add_link(self, obj):
		url = (
			"http://127.0.0.1:8000/"
            + "blogs/"
            + str(obj.id)+"/"
		)
		return format_html('<a class="btn btn-primary" href="{}">Fetch</a>', url)
	add_link.short_description = "Job"
	
 

class BookBlog(admin.ModelAdmin):
    list_display= ('id','get_author_name','title','full_date','description')
    search_fields = ('author__author_name','description')
    list_filter = ('date',)
    
    def full_date(self,obj):
        return obj.date
    full_date.short_description = "Blog Date"
	 
    def get_author_name(self, obj):
        authorobj=Author.objects.get(id=obj.author_id)
        return format_html('<a href="http://127.0.0.1:8000/admin/pyblog/author/?q={}">  {}</a>', obj.author_id,  authorobj.author_name)
    get_author_name.short_description = "Author Name"


		
	
class BookAuthor(admin.ModelAdmin):
	list_display= [field.name for field in Author._meta.fields][:-5]+['get_facebook','get_blogger','get_twitter','get_gmail','get_pinterest']
	search_fields = ('id','author_name')
	def get_facebook(self,obj):
		url = (obj.facebook)
		return  format_html('<a href="{}">facebook</a>', url)
	get_facebook.short_description='facebook id'
	
	def get_blogger(self,obj):
		url = (obj.blogger)
		return  format_html('<a href="{}">blogger</a>', url)
	get_blogger.short_description='blogger id'
	
	def get_twitter(self,obj):
		url = (obj.twitter)
		return  format_html('<a href="{}">twitter</a>', url)
	get_twitter.short_description='twitter id'
	
	def get_gmail(self,obj):
		url = (obj.gmail)
		return  format_html('<a href="{}">gmail</a>', url)
	get_gmail.short_description='gmail id'
	
	def get_pinterest(self,obj):
		url = (obj.pinterest)
		return  format_html('<a href="{}">pinterest</a>', url)
	get_pinterest.short_description='pinterest id'
	
	
	
class BookLog(admin.ModelAdmin):
	list_display=  ('id','get_stat_id','message','time')
	search_fields = ('stat__id',)
	list_filter = ('stat_id',)
	def get_stat_id(self,obj):
		return obj.stat_id
	get_stat_id.short_description='stats id'
	
class BookStats(admin.ModelAdmin):
	list_display = ('id', 'get_job_name', 'status', 'start_time', 'end_time','get_log_details')
	search_fields = ('job__job_name',)
	list_filter = ('job_id',)
	def get_job_name(self, obj):
		job_obj = Job.objects.get(id = obj.job_id)
		return format_html('<a href="http://127.0.0.1:8000/admin/pyblog/job/?q={}">  {}</a>', obj.job_id,  job_obj.job_name)
	get_job_name.short_description = "Job Name"
	
	def get_log_details(self, obj):
		return format_html('<a href="http://127.0.0.1:8000/admin/pyblog/log/?q={}">view log</a>', obj.id )
	get_log_details.short_description = "Logs"	
	
class BookLink(admin.ModelAdmin):
	list_display = [field.name for field in Link._meta.fields][:-2]+[ 'get_blog_name', 'add_link',]
	def add_link(self, obj):
		url = (
			 obj.link_data 
		)
		return format_html('<a href="{}">{}</a>', url,url)
	add_link.short_description = "links"
	def get_blog_name(self,obj):
		blogobj = Blog.objects.get(id=obj.blog_id)
		return blogobj.title
	get_blog_name.short_description = "blog name"	
	
	
admin.site.register(Job,BookJob)
admin.site.register(Blog,BookBlog)
admin.site.register(Log,BookLog)
admin.site.register(Stats,BookStats)
admin.site.register(Link,BookLink)
admin.site.register(Author,BookAuthor)
