from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLES = (
        ('teacher', 'Преподаватель'),
        ('student', 'Студент'),
    )
    role = models.CharField(max_length=10, choices=ROLES,
                            default='student')
    bio = models.TextField(blank=True)


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='courses_taught')
    students = models.ManyToManyField(User,
                                      related_name='courses_enrolled',
                                      blank=True)


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField()
    topic = models.CharField(max_length=200)


class Attendance(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=False)


class Grade(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    comment = models.TextField(blank=True, null=True, default='-')
