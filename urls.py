from django.urls import path, re_path
from django.conf.urls import include
from Easynote import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.view_current_profile, name="view_current_profile"),
    path("profile/delete/", views.delete_current_account, name="delete_current_account"),
    path("profile/export/", views.export_all_notes, name="export_all_notes"),
    path("profile/change_password/", views.change_current_password, name="change_current_password"),
    path("notes/", views.view_available_notes, name="view_available_notes"),
    path("notes/new/", views.create_new_note, name="create_new_note"),
    path("notes/delete/", views.delete_current_note, name="delete_current_note"),
    path("notes/statistics/", views.get_statistics, name="get_statistics"),
    re_path("notes/edit/(?P<name>.+)/", views.edit_current_note, name="edit_current_note"),
    re_path("notes/view/(?P<name>.+)/", views.view_current_note, name="view_current_note"),
    re_path("notes/export/(?P<name>.+)/", views.export_current_note, name="export_current_note"),
    path("notes/search/", views.search_note, name="search_note"),
    path("logout/", views.logout, name="logout"),
]
