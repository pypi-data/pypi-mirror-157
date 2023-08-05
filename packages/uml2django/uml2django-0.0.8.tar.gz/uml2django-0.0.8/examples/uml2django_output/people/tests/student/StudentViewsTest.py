#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from people.models import Student


class StudentViewsTest(TestCase):

    def setUp(self):
        self.student = baker.make(Student)

    def test_student_create_view_status_code(self):
        url = reverse("student-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_student_delete_view_status_code(self):
        url = reverse("student-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_student_detail_view_status_code(self):
        url = reverse("student-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_student_list_view_status_code(self):
        url = reverse("student-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_student_update_view_status_code(self):
        url = reverse("student-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
