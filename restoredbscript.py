import subprocess
import os

DB_URL = "postgresql://neondb_owner:npg_CJM2GvHzl3qT@ep-empty-darkness-ap9njnsv-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
DUMP_FILE = "backup.sql"


def restore_dump_file(dump_file_path):
    """Restore PostgreSQL dump file using pg_restore"""

    if not os.path.exists(dump_file_path):
        print(f"❌ Error: {dump_file_path} not found")
        return False

    try:
        print(f"🔄 Restoring database from {dump_file_path}...")

        result = subprocess.run(
            ["pg_restore", "-d", DB_URL, "-v", dump_file_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Database restored successfully!")
            return True
        else:
            print("❌ Error while restoring database:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    restore_dump_file(DUMP_FILE)


if __name__ == "__main__":
    main()