# Generated by Django 4.2.7 on 2025-03-06 07:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0001_initial'),
        ('matches', '0001_initial'),
        ('venues', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchresult',
            name='mvp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mvp_matches', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='matchparticipant',
            name='match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.match'),
        ),
        migrations.AddField(
            model_name='matchparticipant',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='teams.team'),
        ),
        migrations.AddField(
            model_name='matchparticipant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='match',
            name='away_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='away_matches', to='teams.team'),
        ),
        migrations.AddField(
            model_name='match',
            name='current_players',
            field=models.ManyToManyField(related_name='matches', through='matches.MatchParticipant', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='match',
            name='home_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='home_matches', to='teams.team'),
        ),
        migrations.AddField(
            model_name='match',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_matches', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='match',
            name='venue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='venues.venue'),
        ),
        migrations.AlterUniqueTogether(
            name='matchparticipant',
            unique_together={('match', 'user')},
        ),
    ]
