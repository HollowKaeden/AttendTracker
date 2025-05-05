from django.urls import path, include
from core.views import (SignUpView, DashboardView, TemplateView,
                        CourseDetailView, LessonDetailView)


urlpatterns = [
    path('', TemplateView.as_view(template_name='core/home.html'),
         name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
]
