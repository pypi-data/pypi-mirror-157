#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from infrastructure.models import WorkingPeriod


class WorkingPeriodViewsTest(TestCase):

    def setUp(self):
        self.workingperiod = baker.make(WorkingPeriod)

    def test_workingperiod_create_view_status_code(self):
        url = reverse("workingperiod-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_workingperiod_delete_view_status_code(self):
        url = reverse("workingperiod-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_workingperiod_detail_view_status_code(self):
        url = reverse("workingperiod-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_workingperiod_list_view_status_code(self):
        url = reverse("workingperiod-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_workingperiod_update_view_status_code(self):
        url = reverse("workingperiod-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
