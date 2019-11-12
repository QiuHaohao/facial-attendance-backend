from django.test import TestCase, Client
from django.urls import reverse
from ..views import (CourseViewSet, LabListView, StudentListView, SessionViewSet, AttendanceViewSet,
                     SessionsByLId, sessionBySId, updateAttendanceBySId, updateAttendanceByMId)
from ..models import Course, Lab, Student, Session, Attendance
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils.encoding import force_text


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='admin', email='admin@example.com', password='adminpassword')
        self.client.login(username='admin', password='adminpassword')

        self.student = Student.objects.create(mid="U1622102L", name="test",
                                              email="test@example", face_encoding=b'ab')
        self.course = Course.objects.create(cid="cz3002", year=2019, semester=1,
                                            course_name="Advanced software engineering")
        self.lab = Lab.objects.create(group="TS5", course=self.course)
        self.session = Session.objects.create(lab=self.lab)
        self.attendance = Attendance.objects.create(student=self.student, session=self.session)

    def test_CourseView_by_name(self):
        response = self.client.get(reverse('courses'))
        return self.assertEqual(response.status_code, 200)

    def test_LabListView_by_name(self):
        response = self.client.get(reverse('labs'))
        return self.assertEqual(response.status_code, 200)

    def test_SessionView_by_name(self):
        response = self.client.get(reverse('session'))
        return self.assertEqual(response.status_code, 200)

    def test_StudentListView_by_name(self):
        response = self.client.get(reverse('student'))
        return self.assertEqual(response.status_code, 200)

    def test_sessionBySId(self):
        request = {'sid': self.session.sid}
        response = self.client.get(reverse('session'), request)
        self.assertEqual(response.status_code, 200)

    def test_studentsByMid(self):
        request = {'mid': self.student.mid}
        response = self.client.get(reverse('student'), request)
        self.assertEqual(response.status_code, 200)

    def test_updateAttendanceBySId(self):
        request = {'students': [{'mid': self.student.mid, 'attendance': "A", 'remark': None}], 'sid': self.session.sid}
        response = self.client.post(reverse('attendance_session'), request, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, self.session.sid)

    def test_updateAttendanceByMId(self):
        request = {'sessions': [{'sid': self.session.sid, 'attendance': "A", 'remark': None}], 'mid': self.student.mid}
        response = self.client.post(reverse('attendance_student'), request, content_type="application/json")
        self.assertEqual(response.status_code, 200)
