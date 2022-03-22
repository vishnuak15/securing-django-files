from django.db import migrations

def create_groups(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20190829_1245'),
    ]

    operations = [
        migrations.RunPython(create_groups)
    ]
