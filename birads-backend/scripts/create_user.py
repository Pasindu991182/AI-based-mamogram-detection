"""Create a user account from the command line.

Accounts are provisioned by administrators only, so this is how the very first
admin comes into existence. Usage (from birads-backend/, with the venv active):

    python -m scripts.create_user --email admin@hospital.lk --name "Dr A. Perera" --role admin

The password is prompted for (never passed on the command line, where it would
land in shell history). Add --temporary to force a change at first sign-in.
"""
import argparse
import getpass
import sys

from app.core.security import hash_password, password_policy_error
from app.core.config import settings
from app.db.base import import_models
from app.db.session import SessionLocal, init_db
from app.models.user import ROLE_RADIOLOGIST, ROLES, User


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an ExBI-RADS user account.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", choices=ROLES, default=ROLE_RADIOLOGIST)
    parser.add_argument(
        "--temporary",
        action="store_true",
        help="Require the user to change this password at first sign-in.",
    )
    args = parser.parse_args()
    email = args.email.strip().lower()

    import_models()
    if settings.DATABASE_URL.startswith("sqlite"):
        init_db()  # PostgreSQL tables come from `alembic upgrade head`
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print(f"A user with email {email} already exists.", file=sys.stderr)
            return 1

        password = getpass.getpass("Password: ")
        if password != getpass.getpass("Confirm password: "):
            print("Passwords do not match.", file=sys.stderr)
            return 1
        problem = password_policy_error(password, email)
        if problem:
            print(problem, file=sys.stderr)
            return 1

        user = User(
            email=email,
            name=args.name.strip(),
            role=args.role,
            password_hash=hash_password(password),
            must_change_password=args.temporary,
        )
        db.add(user)
        db.commit()
        print(f"Created {user.role} account #{user.id} for {email}.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
