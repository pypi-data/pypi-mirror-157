#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from educational.models import SubjectLevel


class SubjectLevelViewsTest(TestCase):

    def setUp(self):
        self.subjectlevel = baker.make(SubjectLevel)

    def test_subjectlevel_create_view_status_code(self):
        url = reverse("subjectlevel-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectlevel_delete_view_status_code(self):
        url = reverse("subjectlevel-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectlevel_detail_view_status_code(self):
        url = reverse("subjectlevel-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectlevel_list_view_status_code(self):
        url = reverse("subjectlevel-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectlevel_update_view_status_code(self):
        url = reverse("subjectlevel-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
