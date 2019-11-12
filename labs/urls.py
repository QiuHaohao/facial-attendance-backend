from django.urls import path
from .views import (CourseViewSet, LabListView, StudentListView, StudentDetailView, SessionViewSet, AttendanceViewSet,
                    SessionsByLId, sessionBySId, updateAttendanceBySId, updateAttendanceByMId)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('courses/', CourseViewSet.as_view(), name='courses'),
    path('labs/', LabListView.as_view(), name='labs'),
    path('session/', SessionViewSet.as_view({'get': 'list', 'post': 'create'}), name='session'),
    path('sessions/', SessionsByLId.as_view()),
    path('session/<int:sid>', sessionBySId),
    path('students/', StudentListView.as_view(), name='student'),
    path('student/<str:mid>', StudentDetailView.as_view()),
    path('attendance/session', updateAttendanceBySId, name="attendance_session"),
    path('attendance/student', updateAttendanceByMId, name="attendance_student")
]

urlpatterns.extend(router.urls)
