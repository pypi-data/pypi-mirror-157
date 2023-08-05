#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from educational.models import Subject


class SubjectViewsTest(TestCase):

    def setUp(self):
        self.subject = baker.make(Subject)

    def test_subject_create_view_status_code(self):
        url = reverse("subject-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subject_delete_view_status_code(self):
        url = reverse("subject-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subject_detail_view_status_code(self):
        url = reverse("subject-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subject_list_view_status_code(self):
        url = reverse("subject-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subject_update_view_status_code(self):
        url = reverse("subject-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
