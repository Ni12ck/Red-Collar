from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE INDEX idx_geopoint_location ON points_geopoint USING GIST (location);",
            reverse_sql="DROP INDEX IF EXISTS idx_geopoint_location;",
        ),
    ]
