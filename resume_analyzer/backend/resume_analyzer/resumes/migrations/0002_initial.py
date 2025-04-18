# Generated by Django 5.2 on 2025-04-18 08:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('resumes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resumes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='experience',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experience', to='resumes.resume'),
        ),
        migrations.AddField(
            model_name='education',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to='resumes.resume'),
        ),
        migrations.AddField(
            model_name='resumeanalysis',
            name='resume',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='resumes.resume'),
        ),
        migrations.AddField(
            model_name='resumeskill',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resumes.resume'),
        ),
        migrations.AddField(
            model_name='resumeskill',
            name='skill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resumes.skill'),
        ),
        migrations.AddField(
            model_name='resume',
            name='skills',
            field=models.ManyToManyField(through='resumes.ResumeSkill', to='resumes.skill'),
        ),
        migrations.AlterUniqueTogether(
            name='resumeskill',
            unique_together={('resume', 'skill')},
        ),
    ]
