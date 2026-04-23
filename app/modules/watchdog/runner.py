from __future__ import annotations

from app.modules.watchdog.services.health_probe import build_watchdog_report
from app.modules.watchdog.services.report_writer import (
    write_latest_report,
    write_timestamped_report,
)


def main() -> int:
    report = build_watchdog_report()
    latest_path = write_latest_report(report)
    write_timestamped_report(report)

    print(f"overall_status: {report['overall_status']}")
    print(f"findings_count: {len(report['findings'])}")
    print(f"latest_report: {latest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

