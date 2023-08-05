# Generated by Django 3.1.12 on 2021-09-21 17:54

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="survey", name="category",),
        migrations.RemoveField(model_name="survey", name="validators",),
        migrations.RemoveField(model_name="surveychoice", name="display",),
        migrations.RemoveField(model_name="surveychoice", name="value",),
        migrations.RemoveField(model_name="surveyquestion", name="enforced_notes",),
        migrations.RemoveField(model_name="surveyquestion", name="help_text",),
        migrations.RemoveField(model_name="surveyquestion", name="optional_notes",),
        migrations.RemoveField(model_name="surveyquestion", name="section",),
        migrations.RemoveField(model_name="surveyquestion", name="source",),
        migrations.AddField(
            model_name="survey",
            name="section",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="surveys",
                to="survey.surveysection",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="surveycategory",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="surveychoice",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="surveychoice",
            name="title",
            field=models.CharField(default="What are your allergies ?", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="surveyquestion",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="surveyresponse",
            name="choice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="responses",
                to="survey.surveychoice",
            ),
        ),
        migrations.AddField(
            model_name="surveyresponse",
            name="question",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="responses",
                to="survey.surveyquestion",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="surveyresponse",
            name="value",
            field=models.TextField(default="Sea Food"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="surveysection",
            name="category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sections",
                to="survey.surveycategory",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="surveysection",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="surveyquestion",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="surveyquestion",
            name="type",
            field=models.CharField(
                choices=[
                    ("text", "text (multiple line)"),
                    ("short-text", "short text (one line)"),
                    ("radio", "radio"),
                    ("yes_no", "Yes/No"),
                    ("select", "select"),
                    ("select_image", "Select Image"),
                    ("select_multiple", "Select Multiple"),
                    ("integer", "integer"),
                    ("float", "float"),
                    ("date", "date"),
                ],
                default="radio",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="surveyresponse",
            name="survey",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="responses",
                to="survey.survey",
            ),
        ),
        migrations.AlterField(
            model_name="surveysection",
            name="name",
            field=models.CharField(max_length=200),
        ),
        migrations.DeleteModel(name="SurveyResponseAnswer",),
    ]
