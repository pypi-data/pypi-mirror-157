#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from educational.models import SchoolarPeriod


class SchoolarPeriodViewsTest(TestCase):

    def setUp(self):
        self.schoolarperiod = baker.make(SchoolarPeriod)

    def test_schoolarperiod_create_view_status_code(self):
        url = reverse("schoolarperiod-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_schoolarperiod_delete_view_status_code(self):
        url = reverse("schoolarperiod-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_schoolarperiod_detail_view_status_code(self):
        url = reverse("schoolarperiod-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_schoolarperiod_list_view_status_code(self):
        url = reverse("schoolarperiod-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_schoolarperiod_update_view_status_code(self):
        url = reverse("schoolarperiod-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
