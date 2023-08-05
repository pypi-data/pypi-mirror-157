#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from people.models import Instructor


class InstructorViewsTest(TestCase):

    def setUp(self):
        self.instructor = baker.make(Instructor)

    def test_instructor_create_view_status_code(self):
        url = reverse("instructor-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_instructor_delete_view_status_code(self):
        url = reverse("instructor-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_instructor_detail_view_status_code(self):
        url = reverse("instructor-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_instructor_list_view_status_code(self):
        url = reverse("instructor-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_instructor_update_view_status_code(self):
        url = reverse("instructor-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
