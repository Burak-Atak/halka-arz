import os

SETTINGS = {
    "ACTIVE_NOTIFICATION_TYPES": os.environ.get("ACTIVE_NOTIFICATION_TYPES", "").split(",") if
    os.environ.get("ACTIVE_NOTIFICATION_TYPES", "") else ["telegram"],
    "SCHEDULE_CONFIG": os.environ.get("SCHEDULE_CONFIG") or "0 0 10,13 * * *",
    "TIMEZONE": os.environ.get("TIMEZONE") or "Europe/Istanbul",
}
