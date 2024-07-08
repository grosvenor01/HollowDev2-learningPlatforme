from django.shortcuts import render ,reverse
from django.shortcuts import render , redirect
from .models import profile as prfl 
from .models import *
from django.contrib.auth import authenticate , login
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count , Q
from django.contrib.auth.decorators import user_passes_test
from .schema import schema
import os
from dotenv import load_dotenv
stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.
def register(request):
    if request.method =="GET":
        return render(request, "chat/register.html")
    if request.method == "POST":
        try : 
            username=request.POST.get("username")
            Email = request.POST.get("email")
            password = request.POST.get("password")
            if len(password)<8:
                return render(request, "chat/register.html",context={"Error":"password should be minimum 8 carecters"})
            user = User.objects.create_user(username=username , password=password , email = Email)
            user.save()
            return render(request, "chat/login.html")
        except Exception as e:
            print(e)
            return render(request, "chat/register.html",context={"Error":"Error occured try change the username or email"})


def loging(request):
    if request.method == "GET":
        return render(request, "chat/login.html")
    if request.method =="POST":
        username=request.POST.get("username")
        password = request.POST.get("password")
        user= authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            user = User.objects.get(username=username)
            response =redirect("/home/")
            response.set_cookie('username', username, max_age=360000)
            return response
        else :
            return render(request, "chat/login.html",context={"Error":"you can't login with this credentials"})

@login_required(login_url='/login/')
def home(request):
    try : 
        session_id = request.GET.get('session_id')
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            user=request.user
            course_id = session.metadata.get('course_id')
            course_enrolle =course.objects.get(id=course_id)
            course_enr = course_enrolled.objects.create(enroller = user , course = course_enrolle)
            course_enr.save()
    except Exception as e:
        print(e)
    username = request.COOKIES.get("username")
    user = User.objects.get(username=username)
    enrolled =  course_enrolled.objects.filter(enroller = user)
    couse_enrolleed_b_user=[]
    for i in enrolled:
        couse_enrolleed_b_user.append(i.course)
    courses = [crs for crs in course.objects.all() if crs not in couse_enrolleed_b_user]
    return render(request , "chat/home.html" , context={"courses":courses})

@login_required(login_url='/login/')
def profile(request , pk):
    data = prfl.objects.get(user__username=pk)
    enrolled = course_enrolled.objects.filter(enroller__username=pk)
    return render(request , "chat/profile.html" , context={"profile" : data , "courses":enrolled})
    
@login_required(login_url='/login/')
def enrollment(request , pk):
        localhost_url = 'http://localhost:8000'
        line_items=[]
        try:
            line_item = {
                'quantity': 1,
                'price': course.objects.get(id=pk).price_stripe,
            }
            line_items.append(line_item)
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode="payment",
                payment_method_types =['card',],
                success_url= f'{localhost_url}/home/?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{localhost_url}/profile/',
                metadata={
                'course_id': pk,
                },
            )
        except Exception as e:
            print(e)
        return redirect(checkout_session.url)

@user_passes_test(lambda u: u.is_superuser)
def course_managment(request):
    users = User.objects.all()
    return render(request , "chat/course.html", context={"users":users} )
    
@user_passes_test(lambda u: u.is_superuser)     
def add_permission(request , pk):
    sub_admin_group, created = Group.objects.get_or_create(name='sub_admin')
    if created :
        content_type = ContentType.objects.get_for_model(course)

        permission_1 = Permission.objects.create(
        codename='view_course',
        name='Can view Course',
        content_type=content_type
        )
        permission_2 = Permission.objects.create(
            codename='change_course',
            name='Can change Course',
            content_type=content_type
        )
        permission_2 = Permission.objects.create(
            codename='change_course',
            name='Can change Course',
            content_type=content_type
        )
        sub_admin_group.permissions.add(permission_1, permission_2)
    
    user = User.objects.get(username=pk)
    sub_admin_group.user_set.add(user)

    return redirect(course_managment)
@user_passes_test(lambda u: u.is_superuser)
def remove_permission(request , pk):
    sub_admin_group, created = Group.objects.get_or_create(name='sub_admin')
    
    user = User.objects.get(username=pk)
    sub_admin_group.user_set.remove(user)

    return redirect(course_managment)
@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    user = User.objects.all()
    sub_admin_group = Group.objects.get(name='sub_admin')
    sub_admins = sub_admin_group.user_set.count()
    enrollment = course_enrolled.objects.all()
    course_enrollment_counts = course_enrolled.objects.values('course__Title').annotate(num_users=Count('enroller_id'))
    print(course_enrollment_counts)
    price = 0
    for i in enrollment:
        price += i.course.price
    context = {
        "users":user.count() ,
        "sub_admins":sub_admins , 
        "enrollment":enrollment.count() , 
        "Total_price":round(price,2) , 
        "enrollments":course_enrollment_counts,
    }
    return render(request , "chat/dashboard.html",context=context)

def access_denied(request):
    return render(request, 'chat/403.html')





"""def add_course(request):
    if request.method =="GET":
        return render(request , "chat/form.html")
    elif request.method =="POST":
        course_name = request.POST.get("course-name")
        course_price = request.POST.get("course-price")
        course_description = request.POST.get("course-description")
        num_lessons = int(request.POST.get("num-lessons"))
        owner = User.objects.get(username = request.COOKIES.get("username"))
        course_added = course.objects.create(Title=course_name , owner=owner , descreption=course_description , price = course_price)
        course_added.save()
        csrs = stripe.Product.create(
            name=course_added.Title,
            description=course_added.descreption
        )
        unit_amount = int(float(course_price) * 100)
        price = stripe.Price.create(
            product=csrs.id,
            unit_amount=unit_amount,
            currency='usd',
        )
        course_added.price_stripe = price.id
        course_added.save()
        for i in range(int(num_lessons)):
            lesson_name = request.POST.get("lesson-name-"+str(i+1))
            lesson_content = request.POST.get("lesson-content-"+str(i+1))
            if request.POST.get("lesson-has-quiz-"+str(i+1)) == "on":
                lesson_added =  lesson.objects.create(cours = course_added , title = lesson_name , number=i+1 , content = lesson_content ,have_quiz = "True" )
                lesson_added.save()
                quiz_question = request.POST.get("quiz-question-"+str(i+1))
                quiz_answer1 = request.POST.get("quiz-answer1-"+str(i+1))
                quiz_answer2 = request.POST.get("quiz-answer2-"+str(i+1))
                quiz_answer3 = request.POST.get("quiz-answer3-"+str(i+1))
                quiz_added = quize.objects.create(lesson = lesson_added , question = quiz_question , answer1=quiz_answer1 , answer2=quiz_answer2 , answer3 = quiz_answer3 ,correct = quiz_answer1)
                quiz_added.save()
        return redirect("/home/")"""



# just ignore the solid principales here 
# for those who will review the code i will write a break down here : 
# trying to create course that containe diffrent lessons and each lesson may containe a quize 
# this function or view is only for creating (mutation) query methods are bellow
def add_course(request):
    if request.method == "GET":
        return render(request, "chat/form.html")
    
    elif request.method == "POST":
        course_name = request.POST.get("course-name")
        course_price = request.POST.get("course-price")
        course_description = request.POST.get("course-description")
        num_lessons = int(request.POST.get("num-lessons"))
        owner_username = request.user.username

        create_course_mutation = """
        mutation CreateCourse(
          $courseName: String!,
          $coursePrice: Float!,
          $courseDescription: String!,

          $ownerUsername: String!
        ) {
          createCourse(
            courseName: $courseName,
            coursePrice: $coursePrice,
            courseDescription: $courseDescription,

            ownerUsername: $ownerUsername
          ) {
            course {
              id
              Title
              owner {
                username
              }
              descreption
              price
              priceStripe
            }
          }
        }
        """
        variables = {
            "courseName": course_name,
            "coursePrice": float(course_price),
            "courseDescription": course_description,
            "ownerUsername": owner_username,
        }
        result = schema.execute(create_course_mutation, variables=variables, context=request)

        if result.errors:
            print(result.errors)
            error_messages = [str(error) for error in result.errors]
            return render(request, "chat/form.html", {"errors": error_messages})
        else:
            created_course = result.data["createCourse"]["course"]
            for i in range(num_lessons):
                lesson_name = request.POST.get("lesson-name-"+str(i+1))
                lesson_content = request.POST.get("lesson-content-"+str(i+1))
                create_lesson_mutation = """
                    mutation CreateLesson(
                        $courseId: ID!,
                        $title: String!,
                        $content: String!,
                        $haveQuiz: String!
                    ) {
                        createLesson(
                            courseId: $courseId,
                            title: $title,
                            content: $content,
                            haveQuiz: $haveQuiz
                        ) {
                            lesson {
                                id
                                title
                                cours {
                                    Title
                                }
                                content
                                haveQuiz
                            }
                        }
                    }
                """

                if request.POST.get("lesson-has-quiz-"+str(i+1)) == "on":
                    variables2 = {
                        "courseId": created_course["id"],
                        "title": lesson_name,
                        "content": lesson_content,
                        "haveQuiz": "True",
                    }
                else:
                    variables2 = {
                        "courseId": created_course["id"],
                        "title": lesson_name,
                        "content": lesson_content,
                        "haveQuiz": "False",
                    }

                print(variables2)
                result_lesson = schema.execute(create_lesson_mutation, variables=variables2, context=request)

                if result_lesson.errors:
                    print("Errors:", result_lesson.errors)
                else:
                    created_lesson = result_lesson.data["createLesson"]["lesson"]
                    print("Created lesson:", created_lesson)

                    if request.POST.get("lesson-has-quiz-"+str(i+1)) == "on" :
                        #quiz creation 
                        create_quiz_some = """
                            mutation CreateQuiz(
                               $lessonId :ID!
                               $question :String!
                               $answer1 : String!
                               $answer2 : String!
                               $answer3 : String!
                            ){
                               createQuiz(
                               lessonId : $lessonId
                               question: $question
                               answer1 : $answer1
                               answer2 : $answer2
                               answer3 : $answer3
                               ){
                                 quiz{
                                    id
                                    question 
                                    answer1 
                                    answer2
                                    answer3 
                                    correct 
                                    lesson {
                                        title
                                    }
                                 }
                               }
                            }
                        """
                        variabeles3={
                            "lessonId" : created_lesson["id"],
                            "question": request.POST.get("quiz-question-"+str(i+1)),
                            "answer1" : request.POST.get("quiz-answer1-"+str(i+1)),
                            "answer2" : request.POST.get("quiz-answer2-"+str(i+1)),
                            "answer3" : request.POST.get("quiz-answer3-"+str(i+1)),
                        }
                        print(request.POST.get("quiz-answer1-"+str(i+1)))
                        result_quiz = schema.execute(create_quiz_some , variables=variabeles3 , context=request)
                        if result_quiz.errors:
                            print(result_quiz.errors)
            return redirect(f"/home/")

def get_lessons(request , id): #id of the course 
    query = """ 
    query($coursId: ID!) {
        lessons(coursId: $coursId) {
            title
            id
            cours{
              Title
              descreption
            }
        }
    }
    """
    data = schema.execute(query , variables = {"coursId":id} , context =request)
    return render(request, 'chat/lessons.html' , context=data.data)



def  get_lesson_func(request , id):
    context={}
    query = """ 
    query($lessonId: ID!) {
        lessonById(lessonId: $lessonId) {
            title
            content
            number
            id
            haveQuiz
        }
    }
    """
    data = schema.execute(query , variables = {"lessonId":id} , context =request)

    if data.data.get("lessonById").get("haveQuiz")=="TRUE":
        quiz = quize.objects.get(lesson__id = id)
        context = {
            "lesson":data.data.get("lessonById"),
            "quiz_question": quiz.question,
            "quiz_answer1":quiz.answer1,
            "quiz_answer2":quiz.answer2,
            "quiz_answer3":quiz.answer3,
            "quiz_id":quiz.id
        }
    return context

def get_lesson(request , id): #id ta3 lesson
    context = get_lesson_func(request, id)
    return render(request, "chat/lesson.html", context=context)


def check_quiz(request, id): # id ta3 quiz hna 
    if request.method == "POST":
        selected_answer = request.POST.get("question1")  
        username = request.COOKIES.get("username")
        quiz = quize.objects.get(id=id) 
        lesson = quiz.lesson  
        course = lesson.cours 
        context=get_lesson_func(request , lesson.id)
        print("selected : "+selected_answer)
        lesson_quiz_count = course.lesson_set.filter(have_quiz=True).count()
        
        progress_course = 100 / lesson_quiz_count
        
        enrolled = course_enrolled.objects.get(enroller__username=username, course=course)
        if(enrolled.quiz!=lesson.number):
            enrolled.progress += progress_course
            enrolled.quiz = lesson.number
            enrolled.save()

        if selected_answer != quiz.correct:
            context["wrong"]="the answer is incorrect try again more carefully."
            print(context)
            return render(request, "chat/lesson.html", context=context)
        else:
            context["right"]="Good job!"
            print(context)
            return render(request, "chat/lesson.html", context=context)

