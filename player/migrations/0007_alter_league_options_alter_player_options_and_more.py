# Generated by Django 4.0.4 on 2022-05-02 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0006_remove_league_manager_league_managers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='league',
            options={'ordering': ['name'], 'verbose_name': 'Liga', 'verbose_name_plural': 'Ligen'},
        ),
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ['user__username'], 'verbose_name': 'Spieler', 'verbose_name_plural': 'Spieler'},
        ),
        migrations.AlterField(
            model_name='league',
            name='managers',
            field=models.ManyToManyField(related_name='managed_leagues', to='player.player', verbose_name='Verwalter'),
        ),
        migrations.AlterField(
            model_name='league',
            name='players',
            field=models.ManyToManyField(blank=True, related_name='leagues', to='player.player', verbose_name='Spieler'),
        ),
    ]
