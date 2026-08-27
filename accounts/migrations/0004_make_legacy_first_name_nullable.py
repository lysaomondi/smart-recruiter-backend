"""Allow email-only users in databases created with a legacy first_name column."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_make_legacy_username_nullable"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'accounts_user'
                          AND column_name = 'first_name'
                    ) THEN
                        ALTER TABLE accounts_user
                        ALTER COLUMN first_name DROP NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
