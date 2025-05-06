from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLES = (
        ('teacher', 'Преподаватель'),
        ('student', 'Студент'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default='student',
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Course(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название курса'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        verbose_name='Преподаватель'
    )
    students = models.ManyToManyField(
        User,
        related_name='courses_enrolled',
        blank=True,
        verbose_name='Студенты'
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Курс'
    )
    date = models.DateTimeField(
        verbose_name='Дата и время'
    )
    topic = models.CharField(
        max_length=200,
        verbose_name='Тема занятия'
    )

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
        ordering = ['-date']

    def __str__(self):
        return f"{self.topic} ({self.date:%d.%m.%Y})"


class Attendance(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name='Занятие'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Студент'
    )
    is_present = models.BooleanField(
        default=False,
        verbose_name='Присутствовал'
    )

    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        unique_together = ('lesson', 'student')


class Grade(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name='Занятие'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Студент'
    )
    value = models.IntegerField(
        default=0,
        verbose_name='Оценка'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        default='-',
        verbose_name='Комментарий'
    )

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        unique_together = ('lesson', 'student')
