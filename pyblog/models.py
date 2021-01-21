from django.db import models
import datetime
from django.core.exceptions import ValidationError
# Create your models here.

'''
year_dropdown = []
for y in range(2011, (datetime.datetime.now().year +1)):
    year_dropdown.append((y, y)) 
    
month_dropdown =[]
for indx,y in enumerate(['January', 'Feburary', 'March', 'April', 'May', 'June', 'July','August', 'September', 'October', 'November', 'December']):
    month_dropdown.append((indx, y)) 
    
    
year = models.PositiveSmallIntegerField(('year'), max_length=4, choices=year_dropdown, default=datetime.datetime.now().year)  
month = models.IntegerField(('month'), max_length=10, choices=month_dropdown, default=datetime.datetime.now().month-1,blank=True, null=True)    
'''    
    

class Author(models.Model):
    author_name = models.CharField(max_length=20)
    facebook = models.CharField(max_length=200, blank=True, null=True)
    gmail = models.CharField(max_length=200, blank=True, null=True)
    pinterest = models.CharField(max_length=200, blank=True, null=True)
    twitter = models.CharField(max_length=200, blank=True, null=True)
    blogger = models.CharField(max_length=200, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'Author'


class Blog(models.Model):
    author = models.ForeignKey(Author, models.DO_NOTHING)
    title = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()
  
    class Meta:
        managed = False
        db_table = 'Blog'


class Job(models.Model):
    job_name = models.CharField(max_length=30)
    year = models.PositiveSmallIntegerField()  
    month = models.IntegerField(blank=True, null=True)
    max_fetch = models.PositiveSmallIntegerField(blank=True, null=True)
     
    class Meta:
        managed = False
        db_table = 'Job'
    def clean(self):
        if not(str(self.year).isdigit()):
            raise ValidationError(" Year is numeric")
        elif not( self.year >=2011 and self.year <= datetime.datetime.now().year ):
            raise ValidationError("Year is between 2011 and "+str(datetime.datetime.now().year))
         
        if self.month:
            if not(self.month >= 0 and self.month <= 12):
                raise ValidationError("month is eigther None or  between 0 and 12")
   

class Link(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    link_data = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'Link'

class Stats(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=200)
    end_time = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Stats'


class Log(models.Model):
    stat = models.ForeignKey(Stats, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Log'


