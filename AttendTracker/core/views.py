from django.views.generic import CreateView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.http.response import HttpResponseForbidden
from django.utils.timezone import make_aware
from .models import Course, Lesson, Attendance, Grade
from .forms import SignUpForm, LessonForm, AttendanceForm, GradeForm
import datetime


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == 'teacher':
            context['courses'] = user.courses_taught.all()
            today = make_aware(datetime.datetime.today())
            context['recent_lessons'] = Lesson.objects.filter(
                course__teacher=user
            ).filter(date__gte=today).order_by('date')[:5]

        elif user.role == 'student':
            context['courses'] = user.courses_enrolled.all()

            # Общее количество занятий на всех курсах студента
            total_lessons = Lesson.objects.filter(
                course__students=self.request.user
            ).count()

            # Посещенные занятия
            attended_lessons = Attendance.objects.filter(
                student=self.request.user,
                is_present=True
            ).count()

            context['attendance_stats'] = attended_lessons
            context['total_lessons'] = total_lessons

        return context


class CourseDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Course
    template_name = 'core/course_detail.html'
    context_object_name = 'course'

    def test_func(self):
        course = self.get_object()
        return (self.request.user == course.teacher or
                self.request.user in course.students.all() or
                self.request.user.is_superuser)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lessons'] = (Lesson.objects.filter(course=self.object)
                                            .order_by('-date'))
        context['lesson_form'] = LessonForm()
        return context

    def post(self, request, *args, **kwargs):
        if request.user != self.get_object().teacher:
            return redirect('home')

        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = self.get_object()
            lesson.save()
            for student in lesson.course.students.all():
                Attendance.objects.create(lesson=lesson,
                                          student=student,
                                          is_present=False)
                Grade.objects.create(lesson=lesson,
                                     student=student)
        return redirect('course_detail', pk=self.get_object().pk)


class LessonDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Lesson
    template_name = 'core/lesson_detail.html'
    context_object_name = 'lesson'

    def test_func(self):
        lesson = self.get_object()
        return (self.request.user == lesson.course.teacher or
                self.request.user in lesson.course.students.all() or
                self.request.user.is_superuser)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        students = lesson.course.students.all()

        context['is_teacher'] = self.request.user == lesson.course.teacher
        context['students_data'] = []

        for student in students:
            attendance = Attendance.objects.get(lesson=lesson, student=student)
            grade = Grade.objects.get(lesson=lesson, student=student)

            if self.request.user == lesson.course.teacher:
                # Данные для преподавателя с формами
                context['students_data'].append({
                    'student': student,
                    'attendance_form':
                    AttendanceForm(instance=attendance,
                                   prefix=f'att_{student.id}'),
                    'grade_form': GradeForm(instance=grade,
                                            prefix=f'grade_{student.id}')
                })
            else:
                # Данные для студента без форм
                context['students_data'].append({
                    'student': student,
                    'is_present': attendance.is_present,
                    'grade_value': grade.value,
                    'comment': grade.comment
                })

        return context

    def post(self, request, *args, **kwargs):
        if not self.request.user == self.get_object().course.teacher:
            return HttpResponseForbidden()

        lesson = self.get_object()
        students = lesson.course.students.all()

        # Обработка посещаемости
        for student in students:
            attendance = Attendance.objects.get(
                lesson=lesson,
                student=student
            )
            form = AttendanceForm(
                request.POST,
                instance=attendance,
                prefix=f'att_{student.id}'
            )
            if form.is_valid():
                form.save()

        # Обработка оценок
        for student in students:
            grade = Grade.objects.get(
                lesson=lesson,
                student=student
            )
            form = GradeForm(
                request.POST,
                instance=grade,
                prefix=f'grade_{student.id}'
            )
            if form.is_valid():
                form.save()

        redirect_url = reverse('lesson_detail', kwargs={'pk': lesson.pk})
        if request.GET.get('from') == 'summary':
            redirect_url += '?from=summary'

        messages.success(request, "Изменения успешно сохранены!")
        return redirect(redirect_url)


class CourseSummaryView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Course
    template_name = 'core/course_summary.html'
    context_object_name = 'course'

    def test_func(self):
        course = self.get_object()
        return (self.request.user == course.teacher or
                self.request.user in course.students.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        if self.request.user == course.teacher:
            # Данные для преподавателя
            lessons = course.lesson_set.all().order_by('date')
            students = course.students.all().prefetch_related(
                'attendance_set',
                'grade_set'
            )

            student_data = []
            for student in students:
                attendances = {
                    a.lesson_id: a.is_present
                    for a in student.attendance_set.filter(lesson__in=lessons)
                }
                grades = {
                    g.lesson_id: g.value
                    for g in student.grade_set.filter(lesson__in=lessons)
                }

                total_lessons = lessons.count()
                attended = sum(attendances.values())
                total_grade = sum(grades.values())

                student_data.append({
                    'student': student,
                    'lessons_data': [
                        {
                            'attended': attendances.get(lesson.id, False),
                            'grade': grades.get(lesson.id, 0)
                        } for lesson in lessons
                    ],
                    'total_attended': attended,
                    'attendance_percent': ((attended / total_lessons * 100)
                                           if total_lessons > 0 else 0),
                    'total_grade': total_grade
                })

            context.update({
                'lessons': lessons,
                'student_data': student_data,
                'total_lessons': lessons.count()
            })

        else:
            # Данные для студента
            lessons = course.lesson_set.all().order_by('date')
            attendances = {
                a.lesson_id: a.is_present
                for a in (self.request.user
                          .attendance_set.filter(lesson__in=lessons))
            }
            grades = {
                g.lesson_id: g.value
                for g in self.request.user.grade_set.filter(lesson__in=lessons)
            }

            # Вычисление статистики
            total_lessons = lessons.count()
            attended_lessons = sum(attendances.values())
            total_grade = sum(grades.values())

            context.update({
                'lessons_data': [{
                    'lesson': lesson,
                    'attended': attendances.get(lesson.id, False),
                    'grade': grades.get(lesson.id, 0)
                } for lesson in lessons],
                'attended_lessons': attended_lessons,
                'total_lessons': total_lessons,
                'total_grade': total_grade
            })

        return context
