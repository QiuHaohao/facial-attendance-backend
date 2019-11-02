import os
import json
import numpy as np
import pickle
import base64

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageForm
from rest_framework.exceptions import ParseError
from PIL import Image
import face_recognition
from rest_framework import status, views, parsers, exceptions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser, JSONParser
from rest_framework.decorators import api_view, parser_classes
from .session_manager import handle_recognition_request, read_image_from_request
from labs.models import Student, Session, Lab, Attendance
from labs.serializers import AttendanceSerializer
from .email_service import EmailService

IMG_PATH = 'images'
counter = 0

face_data = {}


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def count_faces(request):
    if 'file' not in request.data:
        raise ParseError("Empty Content")

    f = request.data['file']
    # verify image
    im = Image.open(f)
    im.verify()

    # open image
    im = Image.open(f)
    # if not os.path.exists(IMG_PATH):
    #     os.mkdir(IMG_PATH)
    # im.save(os.path.join(IMG_PATH, 'photo.jpg'))

    im = im.convert('RGB')
    image = np.array(im)
    n_faces = len(face_recognition.face_locations(image))

    global counter
    counter += 1
    return Response(n_faces, status=status.HTTP_200_OK)


@api_view(['POST'])
def end_session(request, *args, **kwargs):
    print("end session")
    es = EmailService()

    if 'sid' not in request.data:
        raise ParseError('No sid found')

    sid = request.data['sid']
    if sid in face_data:
        records = Attendance.objects.filter(session=sid)
        session = Session.objects.get(pk=sid)
        lab = session.lab
        if not records.exists():
            return HttpResponseBadRequest("No records found")

        late_mid = [record.student_id for record in records if record.status == 'L']
        absent_mid = [record.student_id for record in records if record.status == 'AB']

        l_students = Student.objects.filter(pk__in=late_mid)
        ab_students = Student.objects.filter(pk__in=absent_mid)

        for student in l_students:
            es.send_messages(subject="Late for Lab session",
                             template="emailTemplate.html",
                             context={'name': student.name, 'status': "late", 'lab': str(lab)},
                             to_emails=[student.email])
        for student in ab_students:
            es.send_messages(subject="Absent from Lab session",
                             template="emailTemplate.html",
                             context={'name': student.name, 'status': "absent", 'lab': str(lab)},
                             to_emails=[student.email])

        del face_data[sid]
        return Response(sid, status=status.HTTP_200_OK)

    return HttpResponseBadRequest('Session not started')


@api_view(['POST'])
@parser_classes([JSONParser, FormParser])
def post_attendace_img(request, *args, **kwargs):
    if 'image' not in request.data:
        raise ParseError('No image')

    if 'sid' not in request.data:
        raise ParseError('Not sid found')

    # f = request.data['image']
    # try:
    #     im = Image.open(f)
    #     im.verify()
    # except Exception:
    #     raise exceptions.ParseError("Unsupported image")

    # im = Image.open(f)
    # im = im.convert('RGB')
    # im = np.array(im)
    im = read_image_from_request(request.data)

    sid = request.data['sid']
    face_locations = face_recognition.face_locations(im)
    face_encodings = face_recognition.face_encodings(im, face_locations)

    global face_data
    if sid not in face_data:
        session = Session.objects.get(pk=sid)
        students = session.lab.students.all()
        known_face_encodings = [pickle.loads(base64.b64decode(student.face_encoding)) for student in students if student.face_encoding]
        known_face_matric = [student.mid for student in students if student.face_encoding]
        face_data[sid] = {
            'known_face_encodings': known_face_encodings,
            'known_face_matric': known_face_matric,
            'all_students_matric': [student.mid for student in students]
        }

    known_face_encodings = face_data[sid]['known_face_encodings']
    known_face_matric = face_data[sid]['known_face_matric']
    all_students_matric = face_data[sid]['all_students_matric']

    attended_matric = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
        name = 'Unknown'

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_matric[best_match_index]
            attended_matric.append(name)

    status = [True if matric in attended_matric else False for matric in all_students_matric]
    student_status = dict((zip(all_students_matric, status)))

    prev_records = Attendance.objects.filter(session=sid)
    if not prev_records.exists():
        Attendance.objects.bulk_create(
            [Attendance(status='A', student_id=student, session_id=sid) if status
             else Attendance(status='AB', student_id=student, session_id=sid) for student, status in student_status.items()]
        )
    else:
        for record in prev_records:
            # previous record: this student attends the session
            if record.status == 'A':
                pass

            # previous record: this student does not attend session
            elif record.status == 'AB':
                # matches this student, update the status to late
                if student_status[record.student_id]:
                    record.status = 'L'

        Attendance.objects.bulk_update(
            prev_records,
            ['status']
        )

    queryset = Attendance.objects.filter(session=sid)
    serializer = AttendanceSerializer(queryset, many=True)
    return Response(serializer.data)


@csrf_exempt
def index(request):
    json_data = json.loads(request.body.decode("utf-8"))
    if request.method == 'POST':
        n_faces = handle_recognition_request(json_data)
        return JsonResponse({"n_faces": n_faces})
    return HttpResponseBadRequest("Bad Request")


class StudentFaceEncodingView(views.APIView):
    parser_class = (parsers.FileUploadParser,)

    def post(self, request, *args, **kwargs):
        if 'image' not in request.data:
            raise exceptions.ParseError("No image found")
        if 'matric' not in request.data:
            raise exceptions.ParseError("No matric found")

        f = request.data['image']

        try:
            im = Image.open(f)
            im.verify()
        except Exception:
            raise exceptions.ParseError("Unsupported image")

        im = Image.open(f)
        face_image = np.array(im.convert('RGB'))
        face_encoding = face_recognition.face_encodings(face_image)[0]
        face_encoding_bytes = pickle.dumps(face_encoding)
        face_encoding_base64 = base64.b64encode(face_encoding_bytes)

        sid = request.data['matric']
        try:
            student = Student.objects.get(pk=sid)
            student.face_encoding = face_encoding_base64
            student.save()
        except Exception:
            return Response('Error occured', status=status.HTTP_400_BAD_REQUEST)

        return Response(sid, status=status.HTTP_200_OK)
