import time
from datetime import datetime
# import locale
import schedule
from bs4 import BeautifulSoup
from notifications import *
from config import SETTINGS


def check_dates_are_same(date1, date2):
    return date1.day == date2.day and date1.month == date2.month and date1.year == date2.year


def get_data():
    url = "https://halkarz.com/"

    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    halka_arz_list_li_elems = soup.find("ul", {"class": "halka-arz-list"}).find_all("li")
    today = datetime.today()
    actives = []
    for elem in halka_arz_list_li_elems:
        co_li = elem.find("h3", {"class": "il-halka-arz-sirket"})
        a_elem = co_li.find("a")
        company = a_elem.text
        bist_code = elem.find("span", {"class": "il-bist-kod"}).text.strip()
        link = a_elem["href"]
        dates = elem.find("span", {"class": "il-halka-arz-tarihi"}).find("time").text
        if dates == "Hazırlanıyor...":
            continue

        splitted_dates = dates.split(",")
        last_date = splitted_dates[-1]
        year = last_date.split(" ")[-1]
        for dates in dates.split(","):
            dates = dates.strip()
            parsed_days = dates.split(" ")[0].split("-")
            month = dates.split(" ")[1]
            year = dates.split(" ")[2] if len(dates.split(" ")) > 2 else year
            for day in parsed_days[::-1]:
                datetime_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%B-%Y")
                if check_dates_are_same(today, datetime_obj):
                    actives.append({"company": company, "link": link, "dates": dates, "bist_code": bist_code})

                if (
                        datetime_obj.day < today.day or datetime_obj.month < today.month or datetime_obj.year < today.year) and day == \
                        parsed_days[-1]:
                    return actives

    return actives


def main():
    actives = get_data()
    message = "Bugün halka arzı olan şirketler:\n\n"
    for company in actives:
        message += f"{company['bist_code']} - {company['company']} {company['dates']}\n\n"

    if actives:
        notification_types = SETTINGS["ACTIVE_NOTIFICATION_TYPES"]
        for notification_type in notification_types:
            NOTIFICATION_TYPES[notification_type]().send_notification(message)


if __name__ == "__main__":
    # locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    main()

    schedule_times = SETTINGS["SCHEDULE_TIMES"]
    for schedule_time in schedule_times:
        schedule.every().day.at(schedule_time).do(main)
    while True:
        print("Running...")
        schedule.run_pending()
        time.sleep(10)
