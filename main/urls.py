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
    get_education_json,
    register,
    login_user,
    logout_user,
    star_project,
    toggle_star,
    create_project_ajax,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("achievement/", show_achievement, name="show_achievement"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/<uuid:project_id>/delete/",delete_project,name="delete_project"),
    path("projects/star/<uuid:project_id>/", star_project, name="star_project"), 
    path("projects/<uuid:project_id>/star/", toggle_star, name="toggle_star"),
    path('project/<int:pk>/star/', toggle_star, name='toggle_star'),
    path("education/", show_education, name="show_education"),
    path("education/add/", create_education, name="create_education"),
    path("education/<uuid:education_id>/edit/", update_education, name="update_education"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),
    path("education/json/", get_education_json, name="get_education_json"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("projects/add-ajax/", create_project_ajax, name="create_project_ajax"),
]