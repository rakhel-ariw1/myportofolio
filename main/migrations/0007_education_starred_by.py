from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_project_starred_by_project_stars"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="education",
            name="starred_by",
            field=models.ManyToManyField(
                blank=True,
                related_name="starred_educations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
