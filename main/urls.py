from django.urls import path

from main.views import (
    show_main, 
    show_experience, 
    show_achievement,
    create_project,
    show_projects,
    delete_project,
    show_education,
    create_education,
    update_education,
    delete_education,
    get_education_json
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("achievement/", show_achievement, name="show_achievement"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/<uuid:project_id>/delete/",delete_project,name="delete_project"),
    path("education/", show_education, name="show_education"),
    path("education/add/", create_education, name="create_education"),
    path("education/<uuid:education_id>/edit/", update_education, name="update_education"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),
    path("education/json/", get_education_json, name="get_education_json"),
]