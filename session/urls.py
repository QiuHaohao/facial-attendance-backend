from django.urls import path
from .views import post_attendace_img, index, StudentFaceEncodingView, end_session

urlpatterns = [
    path('', index, name='index'),
    path('face/', StudentFaceEncodingView.as_view(), name='student_face'),
    path('image/', post_attendace_img, name="attendance"),
    path('end/', end_session, name="end")
]
