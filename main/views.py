from django.shortcuts import render

from main.models import Experience

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
        "name": "Rakhel",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)