#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from infrastructure.models import ClassRoom


class ClassRoomViewsTest(TestCase):

    def setUp(self):
        self.classroom = baker.make(ClassRoom)

    def test_classroom_create_view_status_code(self):
        url = reverse("classroom-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_classroom_delete_view_status_code(self):
        url = reverse("classroom-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_classroom_detail_view_status_code(self):
        url = reverse("classroom-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_classroom_list_view_status_code(self):
        url = reverse("classroom-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_classroom_update_view_status_code(self):
        url = reverse("classroom-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
