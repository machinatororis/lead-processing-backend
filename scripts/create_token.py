import argparse
from datetime import datetime, timedelta, timezone

from jose import jwt

from core.app.core.config import settings


def create_token(affiliate_id: int) -> str:
    payload = {
        "id": affiliate_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--affiliate-id", type=int, required=True)
    args = parser.parse_args()

    print(create_token(args.affiliate_id))


if __name__ == "__main__":
    main()