from datetime import date

from django.forms import ModelForm, TextInput, Textarea, URLInput, NumberInput, Select

from main.models import Project, Education

from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

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
            )
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

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

    def clean_nama_institusi(self):
        nama_institusi = strip_tags(self.cleaned_data["nama_institusi"]).strip()
        if not nama_institusi:
            raise ValidationError("Nama institusi tidak boleh kosong atau hanya berisi tag HTML.")
        return nama_institusi

    def clean_deskripsi(self):
        return strip_tags(self.cleaned_data.get("deskripsi", "")).strip()

    def clean(self):
        cleaned_data = super().clean()
        tahun_mulai = cleaned_data.get("tahun_mulai")
        tahun_selesai = cleaned_data.get("tahun_selesai")
        maximum_year = date.today().year + 10

        if tahun_mulai and not 1900 <= tahun_mulai <= maximum_year:
            self.add_error(
                "tahun_mulai",
                f"Tahun mulai harus berada di antara 1900 dan {maximum_year}.",
            )
        if tahun_selesai and not 1900 <= tahun_selesai <= maximum_year:
            self.add_error(
                "tahun_selesai",
                f"Tahun selesai harus berada di antara 1900 dan {maximum_year}.",
            )
        if tahun_mulai and tahun_selesai and tahun_selesai < tahun_mulai:
            self.add_error(
                "tahun_selesai",
                "Tahun selesai tidak boleh lebih awal daripada tahun mulai.",
            )

        return cleaned_data
