from datetime import date

from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Education, Project


class ProjectSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "tech_stack", "project_url",
            "project_image_url", "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama proyek tidak boleh kosong.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and request.user in obj.starred_by.all())

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class EducationSerializer(serializers.ModelSerializer):
    jenjang_label = serializers.CharField(source="get_jenjang_display", read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = [
            "id", "nama_institusi", "jenjang", "jenjang_label", "tahun_mulai",
            "tahun_selesai", "deskripsi", "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_nama_institusi(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama institusi tidak boleh kosong.")
        return value

    def validate_deskripsi(self, value):
        return strip_tags(value).strip()

    def validate(self, attrs):
        # PATCH must also validate against the years already stored on the object.
        start = attrs.get("tahun_mulai", getattr(self.instance, "tahun_mulai", None))
        end = attrs.get("tahun_selesai", getattr(self.instance, "tahun_selesai", None))
        maximum_year = date.today().year + 10
        errors = {}
        for field, value in (("tahun_mulai", start), ("tahun_selesai", end)):
            if value is not None and not 1900 <= value <= maximum_year:
                errors[field] = f"Tahun harus berada di antara 1900 dan {maximum_year}."
        if start is not None and end is not None and end < start:
            errors["tahun_selesai"] = "Tahun selesai tidak boleh lebih awal daripada tahun mulai."
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and request.user in obj.starred_by.all())

    def get_starred_by_names(self, obj):
        return [user.username for user in obj.starred_by.all()]
