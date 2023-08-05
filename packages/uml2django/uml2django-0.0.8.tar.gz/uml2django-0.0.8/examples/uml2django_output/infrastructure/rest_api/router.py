import os
from rest_framework import routers
from infrastructure.rest_api.views import (
	BuildingViewSet,
	ClassRoomViewSet,
	WorkingPeriodViewSet
)

router = routers.DefaultRouter()
router.register(
    r'building',
    BuildingViewSet,
    basename="api-building"
)
router.register(
	r'classroom',
	ClassRoomViewSet,
	basename='api-classroom'
)
router.register(
	r'workingperiod',
	WorkingPeriodViewSet,
	basename='api-workingperiod'
)
