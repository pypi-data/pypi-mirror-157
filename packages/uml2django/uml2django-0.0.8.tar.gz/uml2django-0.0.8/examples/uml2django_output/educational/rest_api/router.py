import os
from rest_framework import routers
from educational.rest_api.views import (
	SchoolarPeriodViewSet,
	SubjectViewSet,
	SubjectLevelViewSet,
	SubjectRequirementViewSet,
	SubjectClassViewSet,
	SubjectClassSchedulePeriodViewSet
)

router = routers.DefaultRouter()
router.register(
    r'schoolarperiod',
    SchoolarPeriodViewSet,
    basename="api-schoolarperiod"
)
router.register(
	r'subject',
	SubjectViewSet,
	basename='api-subject'
)
router.register(
	r'subjectlevel',
	SubjectLevelViewSet,
	basename='api-subjectlevel'
)
router.register(
	r'subjectrequirement',
	SubjectRequirementViewSet,
	basename='api-subjectrequirement'
)
router.register(
	r'subjectclass',
	SubjectClassViewSet,
	basename='api-subjectclass'
)
router.register(
	r'subjectclassscheduleperiod',
	SubjectClassSchedulePeriodViewSet,
	basename='api-subjectclassscheduleperiod'
)
