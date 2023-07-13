from django.urls import include, path
from rest_framework import routers
from .views import ClientViewSet, MessageViewSet, MailingStatisticsAPIView, TagViewSet, MyAPIView, MailingViewSet

router = routers.DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'mailings', MailingViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mailing-statistics/', MailingStatisticsAPIView.as_view(), name='mailing-statistics'),
    path('myapi/', MyAPIView.as_view()),
]
