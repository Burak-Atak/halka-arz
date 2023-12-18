import datetime
import pytz
from config import SETTINGS


def get_local_datetime():
    return datetime.datetime.now(pytz.timezone(SETTINGS["TIMEZONE"]))


MONTHS = {
    "Ocak": "1",
    "Şubat": "2",
    "Mart": "3",
    "Nisan": "4",
    "Mayıs": "5",
    "Haziran": "6",
    "Temmuz": "7",
    "Ağustos": "8",
    "Eylül": "9",
    "Ekim": "10",
    "Kasım": "11",
    "Aralık": "12"
}

NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
