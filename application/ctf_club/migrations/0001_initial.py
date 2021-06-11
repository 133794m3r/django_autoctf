# Generated by Django 3.2.4 on 2021-06-11 04:22

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('points', models.IntegerField(default=0)),
                ('tfa_enabled', models.BooleanField(default=False)),
                ('tfa_secret', models.CharField(default=None, max_length=32, null=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Challenges',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('points', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('flag', models.TextField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('num_solves', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='ctf_club.categories')),
            ],
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('filename', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Hints',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('level', models.IntegerField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hints', to='ctf_club.challenges')),
            ],
        ),
        migrations.CreateModel(
            name='Solves',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solves', to='ctf_club.challenges')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solves', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HintsUnlocked',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('hint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ctf_club.hints')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='challenges',
            name='files',
            field=models.ManyToManyField(to='ctf_club.Files'),
        ),
        migrations.AddIndex(
            model_name='categories',
            index=models.Index(fields=['name'], name='ctf_club_ca_name_6766e7_idx'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
