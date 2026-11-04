import datetime
import json

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import F
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from main.forms import EducationForm, ProjectForm
from main.models import Achievement, Education, Experience, Project


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
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "title_query": title_query,
        "form": ProjectForm(),
    }
    return render(request, "project.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('starred_by').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False) 


@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Anda tidak memiliki akses untuk menambah data.")
    
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")

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


@ensure_csrf_cookie
def show_education(request):
    context = {
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "form": EducationForm(),
        "can_edit_education": request.user.is_superuser or is_editor(request.user),
    }
    return render(request, "education.html", context)


@login_required(login_url="/login/")
def create_education(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Hanya pemilik portofolio yang dapat menambah pendidikan.")

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


@login_required(login_url="/login/")
def update_education(request, education_id):
    if not (request.user.is_superuser or is_editor(request.user)):
        return HttpResponseForbidden("Hanya pemilik atau Editor yang dapat mengubah pendidikan.")

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


@login_required(login_url="/login/")
@require_POST
def delete_education(request, education_id):  
    if not request.user.is_superuser:
        return HttpResponseForbidden("Hanya pemilik portofolio yang dapat menghapus pendidikan.")

    pendidikan = get_object_or_404(Education, pk=education_id)

    pendidikan.delete()
    messages.success(request, "Riwayat pendidikan berhasil dihapus!")

    return redirect("main:show_education")


def get_education_json(request):
    search_query = request.GET.get("q", "").strip()
    education_list = Education.objects.prefetch_related("starred_by").order_by(
        "-tahun_mulai",
        "nama_institusi",
    )

    if search_query:
        education_list = education_list.filter(
            Q(nama_institusi__icontains=search_query)
            | Q(jenjang__icontains=search_query)
            | Q(deskripsi__icontains=search_query)
        )

    data = []
    for education in education_list:
        starred_users = list(education.starred_by.all())
        data.append(
            {
                "id": str(education.id),
                "nama_institusi": education.nama_institusi,
                "jenjang": education.jenjang,
                "jenjang_label": education.get_jenjang_display(),
                "tahun_mulai": education.tahun_mulai,
                "tahun_selesai": education.tahun_selesai,
                "deskripsi": education.deskripsi,
                "star_count": len(starred_users),
                "is_starred": (
                    request.user.is_authenticated and request.user in starred_users
                ),
                "starred_by_names": [user.username for user in starred_users],
            }
        )

    return JsonResponse(data, safe=False)


@require_POST
def create_education_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan pendidikan."},
            status=403,
        )

    form = EducationForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

    education = form.save()
    return JsonResponse(
        {
            "message": "Riwayat pendidikan berhasil ditambahkan.",
            "id": str(education.id),
        },
        status=201,
    )


@require_POST
def toggle_education_star(request, education_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"message": "Silakan login untuk memberi star."},
            status=401,
        )

    education = get_object_or_404(Education, pk=education_id)
    is_starred = education.starred_by.filter(pk=request.user.pk).exists()

    if is_starred:
        education.starred_by.remove(request.user)
    else:
        education.starred_by.add(request.user)

    return JsonResponse(
        {
            "is_starred": not is_starred,
            "star_count": education.starred_by.count(),
        }
    )

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

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
