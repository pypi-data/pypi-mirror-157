import os
from rest_framework import routers
from people.rest_api.views import (
	StudentViewSet,
	InstructorViewSet
)

router = routers.DefaultRouter()
router.register(
    r'student',
    StudentViewSet,
    basename="api-student"
)
router.register(
	r'instructor',
	InstructorViewSet,
	basename='api-instructor'
)
