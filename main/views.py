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
        "name": "Rakhel Aqeela Hapsari Ariwibowo",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

Experience.objects.create(
    title="Asisten Dosen Kalkulus 1",
    description="Membantu mahasiswa memahami dasar kalkulus.",
    category="part-time",
)

Experience.objects.create(
    title="Member of Business Growth and Partnership at RISTEK Fasilkom UI",
    description="Membantu growth dan mencari partnership.",
    category="volunteer",
)