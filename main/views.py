from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse

from main.forms import ProjectForm, EducationForm
from main.models import Experience, Achievement, Project, Education


def show_main(request):
    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "npm": "2506605462",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada bisnis."
        ),
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


def create_project(request):
    form = ProjectForm(request.POST or None)

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
    }
    return render(request, "project.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")

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