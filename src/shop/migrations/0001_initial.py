# Generated by Django 3.0.5 on 2020-04-26 10:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sharding.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sharding', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('shardedmodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sharding.ShardedModel')),
                ('name', models.CharField(db_index=True, max_length=120)),
                ('desc', models.CharField(db_index=True, max_length=120)),
                ('slug', models.SlugField(unique=True)),
                ('vendor', sharding.fields.ShardedForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Product',
            },
            bases=('sharding.shardedmodel',),
        ),
    ]