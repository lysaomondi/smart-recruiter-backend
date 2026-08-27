import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attempts', '0001_initial'),
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='attempt',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='result',
                to='attempts.attempt',
            ),
        ),
    ]
