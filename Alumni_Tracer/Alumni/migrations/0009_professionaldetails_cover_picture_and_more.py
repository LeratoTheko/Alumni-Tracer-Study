# Generated by Django 5.0.4 on 2024-06-09 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alumni', '0008_employmentanalysis_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='professionaldetails',
            name='cover_picture',
            field=models.ImageField(blank=True, null=True, upload_to='cover_pictures/'),
        ),
        migrations.AddField(
            model_name='professionaldetails',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]
