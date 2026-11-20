from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),

    path("course/", views.course, name="course"),

    path("course/test/", views.test_view, name="test"),

    path("course/result/", views.result, name="result"),

    path("access-denied/", views.access_denied, name="access_denied"),
]