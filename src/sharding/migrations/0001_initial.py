# Generated by Django 3.0.5 on 2020-05-02 11:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Databases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix', models.CharField(db_index=True, editable=False, max_length=8, unique=True)),
                ('model_name', models.CharField(db_index=True, max_length=20)),
                ('number', models.IntegerField(db_index=True)),
                ('count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ShardedUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('nid', models.CharField(db_index=True, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(db_index=True, max_length=120, unique=True, verbose_name='Username')),
                ('email', models.EmailField(db_index=True, max_length=255, unique=True, verbose_name='email address')),
                ('active', models.BooleanField(default=True)),
                ('staff', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('first_name', models.CharField(max_length=225, verbose_name='First name')),
                ('last_name', models.CharField(max_length=225, verbose_name='First name')),
                ('birth_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
