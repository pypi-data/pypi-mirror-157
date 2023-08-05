# Generated by Django 2.2.24 on 2021-10-15 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0012_usersession"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="creation_time",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="school",
            name="creation_time",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="usersession",
            name="class_field",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="common.Class",
            ),
        ),
        migrations.AddField(
            model_name="usersession",
            name="school",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="common.School",
            ),
        ),
    ]
