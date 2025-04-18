# Generated by Django 5.2 on 2025-04-09 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "verbose_name_plural": "Categories",
            },
        ),
        migrations.AddField(
            model_name="post",
            name="dislikes",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="likes",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="categories",
            field=models.ManyToManyField(
                blank=True, related_name="posts", to="blog.category"
            ),
        ),
    ]
