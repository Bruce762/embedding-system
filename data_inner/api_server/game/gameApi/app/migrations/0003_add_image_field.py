from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_sensor_data_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor_data',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='sensor_images/%Y/%m/%d/'),
        ),
    ] 