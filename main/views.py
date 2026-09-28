from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse

from main.forms import ProjectForm, EducationForm
from main.models import Experience, Achievement, Project, Education

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

import datetime

import json
from django.db.models import F
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied        


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "npm": "2506605462",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada bisnis."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_achievement(request):
    achievement_list = Achievement.objects.all()
    context = {
        'name': 'Rakhel Aqeela Hapsari Ariwibowo',
        'achievement_list': achievement_list,
    }
    return render(request, "achievement.html", context)


@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Anda tidak memiliki akses untuk menambah data.")
    
    form = ProjectForm(request.POST or None)

    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "form": form,
    }
    return render(request, "projects_form.html", context)


def show_projects(request):
    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "project_list": Project.objects.all(),
        'is_editor': is_editor(request.user) if request.user.is_authenticated else False,
    }
    return render(request, "project.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize(
        "json", projects, use_natural_foreign_keys=True  # Tambahkan argumen ini
    )
    return HttpResponse(projects_json, content_type="application/json")


@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Anda tidak memiliki akses untuk menambah data.")
    
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")

    if not request.user.is_superuser:
        raise PermissionDenied

    return redirect("main:show_projects")

@require_POST
def star_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON tidak valid"}, status=400)

    action = data.get("action")
    if action == "star":
        Project.objects.filter(pk=project_id).update(star_count=F("star_count") + 1)
    elif action == "unstar":
        Project.objects.filter(pk=project_id, star_count__gt=0).update(star_count=F("star_count") - 1)
    else:
        return JsonResponse({"error": "Action tidak valid"}, status=400)

    project.refresh_from_db()
    return JsonResponse({"star_count": project.star_count})

# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star
@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")


def show_education(request):
    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "education_list": Education.objects.all().order_by('-tahun_mulai'),
    }
    return render(request, "education.html", context)


def create_education(request):
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil ditambahkan!")
        return redirect("main:show_education")  

    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "form": form,
        "is_update": False,
    }
    return render(request, "education_form.html", context)


def update_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST or None, instance=education)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil diperbarui!")
        return redirect("main:show_education")

    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "form": form,
        "is_update": True,
        "pendidikan": education,
    }
    return render(request, "education_form.html", context)


def delete_education(request, education_id):  
    pendidikan = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        pendidikan.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")

    return redirect("main:show_education")


def get_education_json(request):
    education_list = Education.objects.all()
    education_json = serializers.serialize("json", education_list)
    return HttpResponse(education_json, content_type="application/json")

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Rakhel",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Rakhel",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

def is_editor(user):
    return user.groups.filter(name='Editor').exists()

def is_portfolio_owner(user, project=None):
    if user.is_superuser:
        return True
    if project and hasattr(project, 'user'):
        return project.user == user
    return False

def project_list_json(request):
    projects = Project.objects.all()
    data = [
        {
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'total_stars': p.total_stars(),
        }
        for p in projects
    ]
    return JsonResponse({'projects': data}, safe=False)