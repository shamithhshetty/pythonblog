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
			temp_date=blog.h2.span.string
			blog_date=temp_date[temp_date.find(',')+2:]
			blog_outer = blog.find_all('div',class_="post-outer")
			for outer in blog_outer:
				add_stats_details( stats_id, "Scraping blog data  :  "+str( count )+" ...")
				add_log_details(stats_id,"Scraping blog data   :   "+str( count )+" ...")
				if max_fetch:
					if count>max_fetch :
						break 
				title = outer.h3.a.string 
				description = outer.find("div",class_="post-body")
				author_name = outer.find("div",class_="post-footer").find("span",class_="fn").string
				facebook = outer.find("a",class_="sb-facebook")["href"]
				twitter = outer.find("a",class_="sb-twitter")["href"]
				pinterest = outer.find("a",class_="sb-pinterest")["href"]
				blogger = outer.find("a",class_="sb-blog")["href"]
				gmail = outer.find("a",class_="sb-email")["href"]
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
def get_total_blogs_per_year(year):
	url=URL+"/"+str(year)+"/"
	content = fetch_data(url)
	soup = BeautifulSoup( content, 'html.parser' )
	return len(soup.find_all('div',class_="post-outer"))
def find_start_point_year(start_point,year_list):
	sum_year=0
	start_year=2011
	total_blogs=0
	for year in year_list:
		start_year=year
		total_blogs=get_total_blogs_per_year(year)
		sum_year=sum_year+total_blogs
		if start_point <= sum_year :
			break
	return (start_year,(sum_year-start_point)+1,total_blogs)		
 
	
				
def fetch_blog_data(year,start_point,no_of_fetch,job_id):
	blog_url=URL+"/"+str(year)+"/"
	blog_content = fetch_data(blog_url)
	soup = BeautifulSoup( blog_content, 'html.parser')		
	blogs=soup.find_all('div', class_ = "date-outer")
	count = 1
	fetch=0
	for blog in blogs:
		temp_date=blog.h2.span.string
		blog_date=temp_date[temp_date.find(',')+2:]
		blog_outer = blog.find_all('div',class_="post-outer")
		for outer in blog_outer:
			if start_point > count:
				count=count+1
				continue
			if no_of_fetch == fetch :
				return fetch
				
			title = outer.h3.a.string 
			description = outer.find("div",class_="post-body")
			author_name = outer.find("div",class_="post-footer").find("span",class_="fn").string
			facebook = outer.find("a",class_="sb-facebook")["href"]
			twitter = outer.find("a",class_="sb-twitter")["href"]
			pinterest = outer.find("a",class_="sb-pinterest")["href"]
			blogger = outer.find("a",class_="sb-blog")["href"]
			gmail = outer.find("a",class_="sb-email")["href"]
			#insert data
			authorobj,created = Author.objects.get_or_create(author_name = author_name.strip())
			aobj=Author(id=authorobj.id,author_name = author_name.strip(),facebook =  facebook.strip(), gmail = gmail.strip(), pinterest = pinterest.strip(), twitter = twitter.strip(), blogger = blogger.strip())
			aobj.save()
			blogObj,created = Blog.objects.get_or_create(author = authorobj,title = title, date = datetime.datetime.strptime(blog_date, '%B %d, %Y'),description = str(description.text))
			for link in description.find_all('a'):
				linkobj,created = Link.objects.get_or_create(blog = blogObj, link_data=link['href'])
			fetch=fetch+1
	 
	return fetch
	
def change_start_point(start_point,increment,job_id):
	job_obj=Job.objects.get(id=job_id)
	job_obj.start_point=start_point+increment
	job_obj.save(update_fields=['start_point'])
	
def check_eligible_for_fetch_endpoint(start,end,no_of_fetch):
	if end-start >= no_of_fetch :
		return True
	else:
		return False
			
@shared_task(bind=True)
def extractor( self, job_id, stats_id ):
	fetch_done=0
	job_obj = get_job_data( job_id )  #retrive job details based on job id 
	year_list=[i for i in range(2011,2022)]
	start_year,remaining_blogs,total_blogs= find_start_point_year(job_obj.start_point,year_list)
	if job_obj.no_of_fetch <= remaining_blogs:
		if check_eligible_for_fetch_endpoint(job_obj.start_point-1,job_obj.end_point,job_obj.no_of_fetch) :
			fetch_done=fetch_blog_data(start_year,(total_blogs-remaining_blogs)+1,job_obj.no_of_fetch,job_id)
		else: 
			fetch_done=fetch_blog_data(start_year,(total_blogs-remaining_blogs)+1,(job_obj.end_point-job_obj.start_point)+1,job_id)
	else:
		fetch_done=fetch_blog_data(start_year,(total_blogs-remaining_blogs)+1,remaining_blogs ,job_id)
		for year in range(start_year+1,2021+1):
			remaining_fetch=job_obj.no_of_fetch-fetch_done
			if remaining_fetch <= 0:
				change_start_point(job_obj.start_point,fetch_done,job_id)
				return fetch_done
			total_blogs=get_total_blogs_per_year(year)
			 
			if remaining_fetch <= total_blogs:
				fetch_done=fetch_done + fetch_blog_data(year,1,remaining_fetch ,job_id)
			else: 
				fetch_done=fetch_done + fetch_blog_data(year,1,total_blogs ,job_id)
		
	return  fetch_done

