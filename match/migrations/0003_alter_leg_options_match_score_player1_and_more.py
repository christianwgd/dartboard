# Generated by Django 4.0.3 on 2022-04-11 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0002_match_best_of'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='leg',
            options={'ordering': ['ord'], 'verbose_name': 'Leg', 'verbose_name_plural': 'Legs'},
        ),
        migrations.AddField(
            model_name='match',
            name='score_player1',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Score player 1'),
        ),
        migrations.AddField(
            model_name='match',
            name='score_player2',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Score player 2'),
        ),
    ]
