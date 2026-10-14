"""Test setup: point the app at a throwaway SQLite database before it loads."""
import os
import tempfile

_tmp_dir = tempfile.mkdtemp(prefix="birads-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_dir}/test.db"
os.environ["ENVIRONMENT"] = "test"
os.environ["MAX_FAILED_LOGINS"] = "3"
