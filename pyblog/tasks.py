from celery import shared_task
from bs4 import BeautifulSoup
import urllib.request
from .models import *
import urllib.request
from bs4 import BeautifulSoup
import datetime
import re

URL = "https://blog.python.org"
def convert_month(month):
	return "{0:02d}".format(month+1)
	
def fetch_data(url):
    response = urllib.request.urlopen(url)
    return response.read()
    
def get_job_data(j_id):
	return Job.objects.get(id=j_id)

def get_blog_data(blog_url,max_fetch):
	blog_content=fetch_data(blog_url)
	soup = BeautifulSoup(blog_content, 'html.parser')
	blogs=soup.find_all('div',class_="date-outer")
	count=1
	for blog in blogs:
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
		authorobj,created = Author.objects.get_or_create(author_name = author_name.strip(), facebook =  facebook.strip(), gmail = gmail.strip(), pinterest = pinterest.strip(), twitter = twitter.strip(), blogger = blogger.strip() )
		blogObj,created = Blog.objects.get_or_create(author=authorobj,title=title,date=datetime.datetime.strptime(blog_date, '%B %d, %Y'),description=str(description))
		for link in description.find_all('a'):
			linkobj,created=Link.objects.get_or_create(blog = blogObj, link_data=link['href'])
		count=count+1
	return count-1
			 
def get_data_with_month_year(job_obj):
	blog_url = URL + "/" + str(job_obj.year) + "/" + str(convert_month(job_obj.month)) + "/"
	s=get_blog_data(blog_url,job_obj.max_fetch)
	return s
	
	
def get_data_with_year(job_obj):
	blog_url = URL + "/" + str(job_obj.year) + "/"
	blog_content=fetch_data(blog_url)
	soup = BeautifulSoup(blog_content, 'html.parser')
	data= soup.find_all('a', {'href': re.compile('blogspot.com/'+str(job_obj.year)+'/')})
	list_month=set()
	for link in data:
		txt=link['href']
		x = txt.find("2013")
		list_month.add(txt[x+5:x+7])
	return list_month


@shared_task(bind=True)
def scrape(self, job_id):
	job_obj=get_job_data(job_id)  #retrive job details based on job id 
	if job_obj.month and job_obj.year:
		s=get_data_with_month_year(job_obj)
	elif job_obj.year:
		s=get_data_with_year(job_obj)
	return s
