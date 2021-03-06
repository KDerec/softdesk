# Generated by Django 4.0.5 on 2022-06-29 14:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Projects",
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
                    "project_id",
                    models.IntegerField(help_text="Numéro d'identifiant du projet."),
                ),
                (
                    "title",
                    models.CharField(help_text="Titre du projet.", max_length=128),
                ),
                (
                    "description",
                    models.CharField(
                        help_text="Description du projet.", max_length=2048
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        help_text="Type du projet (back-end, front-end, iOS ou Android).",
                        max_length=128,
                    ),
                ),
                (
                    "author_user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Contributors",
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
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
