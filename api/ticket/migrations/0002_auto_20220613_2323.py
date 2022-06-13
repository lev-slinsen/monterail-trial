# Generated by Django 3.2.13 on 2022-06-13 23:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_auto_20220613_2323'),
        ('reservation', '0002_auto_20220613_2323'),
        ('ticket', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='event_row',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='event.eventrow'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='reservation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets', to='reservation.reservation'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='seat',
            field=models.SmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]