from django.urls import path

from main.views import (
    show_main, 
    show_experience, 
    show_achievement,
    create_project,
    show_projects,
    delete_project
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("achievement/", show_achievement, name="show_achievement"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/<uuid:project_id>/delete/",delete_project,name="delete_project"),
]