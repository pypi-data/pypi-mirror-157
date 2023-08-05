#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from educational.models import SubjectClass


class SubjectClassViewsTest(TestCase):

    def setUp(self):
        self.subjectclass = baker.make(SubjectClass)

    def test_subjectclass_create_view_status_code(self):
        url = reverse("subjectclass-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectclass_delete_view_status_code(self):
        url = reverse("subjectclass-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectclass_detail_view_status_code(self):
        url = reverse("subjectclass-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectclass_list_view_status_code(self):
        url = reverse("subjectclass-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectclass_update_view_status_code(self):
        url = reverse("subjectclass-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
