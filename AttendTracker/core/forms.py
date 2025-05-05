from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Lesson, Attendance, Grade


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLES)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')


class LessonForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
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
