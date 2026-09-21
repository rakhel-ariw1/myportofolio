from django.forms import ModelForm, TextInput, Textarea, URLInput, NumberInput, Select

from main.models import Project, Education

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }

class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "nama_institusi",
            "jenjang",
            "tahun_mulai",
            "tahun_selesai",
            "deskripsi",
        ]

        labels = {
            "nama_institusi": "Nama Institusi",
            "jenjang": "Jenjang",
            "tahun_mulai": "Tahun Mulai",
            "tahun_selesai": "Tahun Selesai",
            "deskripsi": "Deskripsi",
        }

        widgets = {
            "nama_institusi": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "jenjang": Select(),
            "tahun_mulai": NumberInput(
                attrs={
                    "placeholder": "2025",
                }
            ),
            "tahun_selesai": NumberInput(
                attrs={
                    "placeholder": "2029 (kosongkan jika masih berjalan)",
                }
            ),
            "deskripsi": Textarea(
                attrs={
                    "placeholder": "Ceritakan pengalaman pendidikanmu",
                    "rows": 3,
                }
            ),
        }