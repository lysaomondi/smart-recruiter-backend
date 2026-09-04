# Reconciles databases where accounts.0001_initial was recorded before the
# full_name column existed on accounts_user.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE accounts_user
                        ADD COLUMN IF NOT EXISTS full_name varchar(150);

                        UPDATE accounts_user
                        SET full_name = LEFT(SPLIT_PART(email, '@', 1), 150)
                        WHERE full_name IS NULL OR full_name = '';

                        ALTER TABLE accounts_user
                        ALTER COLUMN full_name SET NOT NULL;
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[],
        ),
    ]
