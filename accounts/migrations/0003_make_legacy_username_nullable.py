"""Allow email-only users in databases created with a legacy username column."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_add_missing_full_name_column"),
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
                          AND column_name = 'username'
                    ) THEN
                        ALTER TABLE accounts_user
                        ALTER COLUMN username DROP NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
