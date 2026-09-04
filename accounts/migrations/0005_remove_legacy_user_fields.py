from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_make_legacy_first_name_nullable"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE accounts_user
                DROP COLUMN IF EXISTS username,
                DROP COLUMN IF EXISTS first_name,
                DROP COLUMN IF EXISTS last_name,
                DROP COLUMN IF EXISTS date_joined;
            """,
            reverse_sql="""
                ALTER TABLE accounts_user
                ADD COLUMN IF NOT EXISTS username varchar(150) NULL,
                ADD COLUMN IF NOT EXISTS first_name varchar(150) NULL,
                ADD COLUMN IF NOT EXISTS last_name varchar(150) NULL,
                ADD COLUMN IF NOT EXISTS date_joined timestamp with time zone NULL;
            """,
        ),
    ]
