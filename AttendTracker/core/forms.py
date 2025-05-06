from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Lesson, Attendance, Grade


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'  # Устанавливаем роль по умолчанию
        if commit:
            user.save()
        return user


class LessonForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Дата'
    )

    class Meta:
        model = Lesson
        fields = ['date', 'topic']


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['is_present']
        widgets = {
            'is_present': forms.CheckboxInput(attrs={'class':
                                                     'form-check-input'})
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['value', 'comment']
        widgets = {
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Комментарий...'
            })
        }
