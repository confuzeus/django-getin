# Generated by Django 4.0.1 on 2022-01-17 19:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Invitation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        max_length=64, unique=True, verbose_name="Invitation code"
                    ),
                ),
                ("state", django_fsm.FSMField(default="Unsent", max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="getin_invitation",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "getin_invitations",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="invitation",
            index=models.Index(
                fields=["created_at"], name="getin_invit_created_9eb192_idx"
            ),
        ),
    ]