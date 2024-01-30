# Generated by Django 5.0.1 on 2024-01-23 04:15

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BookPublication",
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
                ("faculty_id", models.CharField(max_length=20)),
                ("title_of_book", models.CharField(max_length=255)),
                ("issbn", models.CharField(max_length=20)),
                ("date_published", models.DateField()),
                ("doi_link", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="Certification",
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
                ("faculty_id", models.CharField(max_length=20)),
                ("name_of_certification", models.CharField(max_length=255)),
                ("certification_authority", models.CharField(max_length=255)),
                ("date", models.DateField()),
                ("url", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="ConferencePublication",
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
                ("faculty_id", models.CharField(max_length=20)),
                ("name_of_conference_attended", models.CharField(max_length=255)),
                ("paper_entitled", models.CharField(max_length=255)),
                ("from_date", models.DateField()),
                ("to_date", models.DateField()),
                ("url", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="JournalPublication",
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
                ("faculty_id", models.CharField(max_length=20)),
                ("title_of_publication", models.CharField(max_length=255)),
                ("name_of_journal", models.CharField(max_length=255)),
                ("date_published", models.DateField()),
                ("url", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="Patent",
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
                ("faculty_faculty_id", models.CharField(max_length=20)),
                ("title_of_innovation", models.CharField(max_length=255)),
                ("application_no", models.CharField(max_length=255)),
                ("date", models.DateField()),
                ("url", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="Faculty",
            fields=[
                (
                    "faculty_id",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("password", models.CharField(max_length=255)),
                ("position", models.CharField(max_length=255)),
                ("department", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("date_of_joining", models.DateField()),
                ("is_hod", models.BooleanField(default=False)),
                (
                    "book_publications",
                    models.ManyToManyField(to="facultyDataManager.bookpublication"),
                ),
                (
                    "certifications",
                    models.ManyToManyField(to="facultyDataManager.certification"),
                ),
                (
                    "conference_publications",
                    models.ManyToManyField(
                        to="facultyDataManager.conferencepublication"
                    ),
                ),
                (
                    "journal_publications",
                    models.ManyToManyField(to="facultyDataManager.journalpublication"),
                ),
                ("patents", models.ManyToManyField(to="facultyDataManager.patent")),
            ],
        ),
    ]
