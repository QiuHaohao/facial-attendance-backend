from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from labs.models import Student, Session, Course, Lab

import os
import base64


class TestPostAttendanceImage(TestCase):
    def setUp(self):
        course = Course.objects.create(cid="CZ3002", year=2019, semester=1,
                                       course_name="ASE")
        lab = Lab.objects.create(group='TS5', course=course)
        self.session = Session.objects.create(lab=lab)
        self.student1 = Student.objects.create(mid='U1622102L', name='test1', email='test1@example.com')
        self.student2 = Student.objects.create(mid='U1622102J', name='test2', email='test2@example.com')
        self.student1.lab.add(lab)
        self.student2.lab.add(lab)
        self.client = Client()
        # create admin account for authendication
        User.objects.create_user(username='test', email='admin@example.com', password='adminpassword')
        self.client.login(username='test', password='adminpassword')

        # store student's face encoding
        with open(os.path.join(os.path.dirname(__file__), 'studentImage1.jpg'), 'rb') as f:
            response = self.client.post(reverse('student_face'), {'mid': 'U1622102L', 'image': f})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with open(os.path.join(os.path.dirname(__file__), 'studentImage2.jpg'), 'rb') as f:
            response = self.client.post(reverse('student_face'), {'mid': 'U1622102J', 'image': f})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testPostAttendanceImage_s1As2AB_success(self):
        header = "base64"
        with open(os.path.join(os.path.dirname(__file__), 'studentImage1.jpg'), 'rb') as f:
            encodedImg = "{},{}".format(header, str(base64.b64encode(f.read()), 'utf-8'))

        response = self.client.post(reverse('attendance'), {'sid': self.session.sid, 'image': encodedImg}, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mids = [entry['student'] for entry in response.data]
        sessionStatus = [entry['status'] for entry in response.data]

        self.assertEqual(sessionStatus[mids.index(self.student1.mid)], 'A')
        self.assertEqual(sessionStatus[mids.index(self.student2.mid)], 'AB')

    def testPostAttendanceImage_s1As2L_success(self):
        header = "base64"
        # previous session record
        with open(os.path.join(os.path.dirname(__file__), 'studentImage1.jpg'), 'rb') as f:
            encodedImg = "{},{}".format(header, str(base64.b64encode(f.read()), 'utf-8'))
            self.client.post(reverse('attendance'), {'sid': self.session.sid, 'image': encodedImg}, content_type="application/json")

        with open(os.path.join(os.path.dirname(__file__), 'studentImage2.jpg'), 'rb') as f:
            encodedImg = "{},{}".format(header, str(base64.b64encode(f.read()), 'utf-8'))

        response = self.client.post(reverse('attendance'), {'sid': self.session.sid, 'image': encodedImg}, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mids = [entry['student'] for entry in response.data]
        sessionStatus = [entry['status'] for entry in response.data]

        self.assertEqual(sessionStatus[mids.index(self.student1.mid)], 'A')
        self.assertEqual(sessionStatus[mids.index(self.student2.mid)], 'L')
