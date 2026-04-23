from __future__ import annotations

import json

from app.modules.partners.services.engagement_analytics import (
    build_engagement_analytics_report,
)


def main() -> int:
    print(
        json.dumps(
            build_engagement_analytics_report(),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
