from celery import shared_task
from bs4 import BeautifulSoup
import urllib.request
from .models import *
import urllib.request
from bs4 import BeautifulSoup
import datetime
import re
import time


URL = "https://blog.python.org"
def convert_month(month):
	return "{0:02d}".format(month)
	
def fetch_data(url):
    response = urllib.request.urlopen(url)
    return response.read()
    
def get_job_data(j_id):
	return Job.objects.get(id = j_id)
	
def add_stats_details( stats_id, msg ):
	stats_obj = Stats.objects.get( id = stats_id )
	stats_obj.status = msg
	stats_obj.save( update_fields = ['status'])
	
def add_log_details( stats_id, msg ):
	log_obj = Log.objects.create( stat_id = stats_id , message = msg, time = datetime.datetime.now() )
	

def get_blog_data( blog_url, max_fetch, stats_id, filename ):
	blog_content = fetch_data(blog_url)
	#creating file
	soup = BeautifulSoup( blog_content, 'html.parser' )
	file_ptr = open( "blog_files/" + filename + ".txt", "w" )
	file_ptr.write( str( soup ))
	file_ptr.close()
	
	blogs=soup.find_all('div', class_ = "date-outer")
	count = 1
	add_stats_details(stats_id, "Total ( "+str(len(blogs))+" ) Blogs found...")
	add_log_details(stats_id, "Total ( "+str(len(blogs))+" ) Blogs found and max fetch is "+str(max_fetch))
	for blog in blogs:
		try:
			add_stats_details( stats_id, "Scraping blog data  :  "+str( count )+" ...")
			add_log_details(stats_id,"Scraping blog data   :   "+str( count )+" ...")
			if max_fetch:
				if count>max_fetch :
					break 
			temp_date=blog.h2.span.string
			blog_date=temp_date[temp_date.find(',')+2:]
			title = blog.find('div',class_="post-outer").h3.a.string 
			description = blog.find("div",class_="post-body")
			author_name = blog.find("div",class_="post-footer").find("span",class_="fn").string
			facebook = blog.find("a",class_="sb-facebook")["href"]
			twitter = blog.find("a",class_="sb-twitter")["href"]
			pinterest = blog.find("a",class_="sb-pinterest")["href"]
			blogger = blog.find("a",class_="sb-blog")["href"]
			gmail = blog.find("a",class_="sb-email")["href"]
			#insert data
			authorobj,created = Author.objects.get_or_create(author_name = author_name.strip())
			aobj=Author(id=authorobj.id,author_name = author_name.strip(),facebook =  facebook.strip(), gmail = gmail.strip(), pinterest = pinterest.strip(), twitter = twitter.strip(), blogger = blogger.strip())
			aobj.save()
			blogObj,created = Blog.objects.get_or_create(author = authorobj,title = title, date = datetime.datetime.strptime(blog_date, '%B %d, %Y'),description = str(description.text))
			for link in description.find_all('a'):
				linkobj,created = Link.objects.get_or_create(blog = blogObj, link_data=link['href'])
			count=count+1
		except:
			add_stats_details( stats_id, "ERROR : unable to fetch data : Blog NO :  :  "+str( count )+" ...")
			add_log_details(stats_id,"ERROR : unable to fetch data : Blog NO :  :  "+str( count )+" ...")
	try:
		stats_obj=Stats.objects.get(id=stats_id)
		stats_obj.status="Scraping blog data completed. Total blogs fetched : "+str(count-1)
		stats_obj.end_time=datetime.datetime.now() 
		stats_obj.save(update_fields=['status','end_time'])
		add_log_details(stats_id,"Scraping blog data completed. Total blogs fetched :  "+str(count-1))
	except:
		add_stats_details( stats_id, "ERROR : unable to update states data ")
		add_log_details(stats_id,"ERROR : unable to update states data ")
	return count-1
			 
def get_data_with_month_year( job_obj, stats_id, filename ):
	blog_url = URL + "/" + str( job_obj.year ) + "/" + str( convert_month( job_obj.month )) + "/"
	s = get_blog_data(blog_url, job_obj.max_fetch, stats_id, filename)
	return s
	
	
def get_data_with_year(job_obj,stats_id,filename):
	blog_url = URL + "/" + str( job_obj.year ) + "/"
	s=get_blog_data( blog_url, job_obj.max_fetch, stats_id,filename )
	return s
	
	'''
	blog_content=fetch_data(blog_url)
	soup = BeautifulSoup(blog_content, 'html.parser')
	data= soup.find_all('a', {'href': re.compile('blogspot.com/'+str(job_obj.year)+'/')})
	list_month=set()
	for link in data:
		txt=link['href']
		x = txt.find(str(job_obj.year))
		list_month.add(txt[x+5:x+7])
	for month_id in list_month:
		if month_id != " " or month_id != '' :
			get_blog_data(blog_url+str(month_id)+"/",10)
	return list_month
	'''

@shared_task(bind=True)
def scrape( self, job_id, stats_id ):
	job_obj = get_job_data( job_id )  #retrive job details based on job id 
	add_stats_details( stats_id, "Checking YEAR="+str(job_obj.year)+" and MONTH "+ str(job_obj.month))
	add_log_details(stats_id,"Checking YEAR="+str(job_obj.year)+" and MONTH "+ str(job_obj.month))
	if job_obj.month and job_obj.year:
		filename = str( job_id )+"_"+str( job_obj.month )+"_"+str( job_obj.year )
		s = get_data_with_month_year( job_obj,stats_id,filename )
	elif job_obj.year:
		filename = str( job_id ) +"_"+str( job_obj.year )
		s = get_data_with_year( job_obj, stats_id, filename )
	return str(s)+"  records fetched successfully" 
