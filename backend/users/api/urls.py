from django.urls import include, path

from users.api.views import UserProfileView

urlpatterns = [
    path("auth/", include("users.api.auth.urls")),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
]
