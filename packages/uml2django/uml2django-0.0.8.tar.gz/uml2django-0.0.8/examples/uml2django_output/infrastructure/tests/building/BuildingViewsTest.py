#Core Django imports
from django.test import TestCase
from django.urls import reverse

#Third-party app imports
from model_bakery import baker

from infrastructure.models import Building


class BuildingViewsTest(TestCase):

    def setUp(self):
        self.building = baker.make(Building)

    def test_building_create_view_status_code(self):
        url = reverse("building-create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_building_delete_view_status_code(self):
        url = reverse("building-delete",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_building_detail_view_status_code(self):
        url = reverse("building-detail",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_building_list_view_status_code(self):
        url = reverse("building-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    def test_building_update_view_status_code(self):
        url = reverse("building-update",  args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
