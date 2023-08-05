#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from educational.models import SubjectClassSchedulePeriod


class SubjectClassSchedulePeriodViewsTest(TestCase):

    def setUp(self):
        self.subjectclassscheduleperiod = baker.make(SubjectClassSchedulePeriod)

    def test_subjectclassscheduleperiod_create_view_status_code(self):
        url = reverse("subjectclassscheduleperiod-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectclassscheduleperiod_delete_view_status_code(self):
        url = reverse("subjectclassscheduleperiod-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectclassscheduleperiod_detail_view_status_code(self):
        url = reverse("subjectclassscheduleperiod-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectclassscheduleperiod_list_view_status_code(self):
        url = reverse("subjectclassscheduleperiod-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_subjectclassscheduleperiod_update_view_status_code(self):
        url = reverse("subjectclassscheduleperiod-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
