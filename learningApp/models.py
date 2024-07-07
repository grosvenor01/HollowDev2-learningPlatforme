from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
User = get_user_model()

class profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    description = models.TextField()
    joined_us = models.DateTimeField(auto_now=True)
    specilality = models.CharField(max_length=30)
    #as i don't have a lot of data or unused data to send to the frontend 
    #i am adding this two to just add graphql functionality 
    idk = models.CharField(max_length=30)
    idk2 = models.CharField(max_length=50)
class course(models.Model):
    owner = models.ForeignKey(User , on_delete=models.CASCADE)
    Title =  models.CharField(max_length=100)
    descreption = models.TextField()
    date = models.DateField(auto_now=True)
    price = models.FloatField(validators=[MinValueValidator(0)])
    price_stripe = models.CharField(max_length=200 , blank=True)

class course_enrolled(models.Model):
    enroller = models.ForeignKey(User , on_delete=models.CASCADE)
    course = models.ForeignKey(course , on_delete=models.CASCADE)
    progress = models.FloatField(validators=[MaxValueValidator(100) , MinValueValidator(0)] , default=0)
    quiz = models.IntegerField(default=0)
class lesson(models.Model):
     cours =  models.ForeignKey(course , on_delete=models.CASCADE)
     title = models.CharField(max_length=100)
     number =  models.IntegerField(validators=[MaxValueValidator(100) , MinValueValidator(1)])
     have_quiz = models.CharField(max_length=10 , choices=(("True","True"),("False","False")))
     content = models.TextField() 
class quize(models.Model):
    lesson = models.OneToOneField(lesson , on_delete=models.CASCADE)
    question = models.CharField(max_length = 200)
    answer1 = models.CharField(max_length=100)
    answer2 = models.CharField(max_length=100)
    answer3 = models.CharField(max_length=100)
    correct = models.CharField(max_length=100)

@receiver(post_save, sender=User) 
def create_profile(sender, instance, created, **kwargs):
        if created:
            descreption = " i add this for testing the graphql only you ccan modify it from the admin panel "
            specilality = " bnadem no life maandouch speciality (jk had data creyitha b signal tssema random)"
            idk = " hna aslan manaach rayhin nsh9ouha tssema 3amer brk"
            idk2 = " same "
            prfl = profile.objects.create(user=instance ,description=descreption,specilality=specilality , idk = idk , idk2=idk2)
            prfl.save()
            

