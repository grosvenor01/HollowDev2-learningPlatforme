import graphene
import graphene_django
from .models import *
import stripe 
from django.conf import settings

class UserType(graphene_django.DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"

class QuizType(graphene_django.DjangoObjectType):
    class Meta:
        model = quize
        fields = "__all__"

class CourseType(graphene_django.DjangoObjectType):
    owner = graphene.Field(UserType)
    class Meta:
        model = course
        fields = "__all__"

class LessonType(graphene_django.DjangoObjectType):
    cours = graphene.Field(CourseType)
    class Meta:
        model = lesson
        fields = "__all__"


class Query(graphene.ObjectType):
    quizes = graphene.List(QuizType)
    courses = graphene.List(CourseType)
    lessons = graphene.List(LessonType, coursId=graphene.ID())
    lesson_by_id = graphene.Field(LessonType, lesson_id=graphene.ID(required=True))

    def resolve_lessons(self, info, coursId):
        return lesson.objects.filter(cours__id=coursId)
    
    def resolve_lesson_by_id(self, info, lesson_id):
        try:
            return lesson.objects.get(id=lesson_id)
        except lesson.DoesNotExist:
            return None


class CreateCourse(graphene.Mutation):
    course = graphene.Field(CourseType)

    class Arguments:
        courseName = graphene.String(required=True)
        coursePrice = graphene.Float(required=True)
        courseDescription = graphene.String(required=True)
        ownerUsername = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, courseName, coursePrice, courseDescription,  ownerUsername):
        owner = User.objects.get(username=ownerUsername)
        cours = course.objects.create(
            owner=owner,
            Title=courseName,
            descreption=courseDescription,
            price=coursePrice,
        )
        cours.save()
        stripe.api_key = settings.STRIPE_SECRET_KEY
        csrs = stripe.Product.create(
            name=cours.Title,
            description=cours.descreption
        )
        unit_amount = int(float(coursePrice) * 100)
        price = stripe.Price.create(
            product=csrs.id,
            unit_amount=unit_amount,
            currency='usd',
        )
        cours.price_stripe = price.id
        cours.save()
        return CreateCourse(course=cours)


class CreateLesson(graphene.Mutation):
    lesson = graphene.Field(LessonType)
    course = graphene.Field(CourseType)

    class Arguments:
        courseId = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        haveQuiz = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, courseId, title, content, haveQuiz):
        course_obj = course.objects.get(id=courseId)
        lesson_added = lesson.objects.create(
            cours=course_obj,
            title=title,
            number=lesson.objects.filter(cours=course_obj).count() + 1,
            content=content,
            have_quiz=haveQuiz
        )
        lesson_added.save()
        return CreateLesson(lesson=lesson_added, course=course_obj)



class CreateQuiz(graphene.Mutation):
    quiz = graphene.Field(QuizType)
    lesson = graphene.Field(LessonType)
    class Arguments:
        lessonId = graphene.ID(required=True)
        question = graphene.String(required=True)
        answer1 = graphene.String(required=True)
        answer2 = graphene.String(required=True)
        answer3 = graphene.String(required=True)

    def mutate(self, info, lessonId , question , answer1 , answer2 , answer3):
        lessoni = lesson.objects.get(id=lessonId)
        quiz_added = quize.objects.create(
            lesson=lessoni,
            question=question,
            answer1=answer1,
            answer2=answer2,
            answer3=answer3,
            correct=answer1
        )
        quiz_added.save()
        return CreateQuiz(quiz=quiz_added)

class Mutation(graphene.ObjectType):
    create_course = CreateCourse.Field()
    create_lesson = CreateLesson.Field()
    create_quiz = CreateQuiz.Field()


schema = graphene.Schema(query=Query , mutation=Mutation)