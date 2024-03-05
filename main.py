from datetime import datetime
import requests
from bs4 import BeautifulSoup
from helper import MONTHS, NUMBER_EMOJIS, get_local_datetime


def check_dates_are_same(date1, date2):
    return date1.day == date2.day and date1.month == date2.month and date1.year == date2.year


def time_range(soup):
    class_name = "fa-regular fa-clock"
    elem = soup.find("i", {"class": class_name})
    return elem.parent.text if elem else ""


def get_price(soup):
    class_name = "f700"
    return soup.find("strong", {"class": class_name}).text


def get_possible_lots(soup):
    h5 = "Dağıtılacak Pay Miktarı (Olası) *"
    li = soup.find("h5", string=h5).parent
    if not li:
        return

    p = li.find("p")
    all_brs = p.find_all("br")
    possible_lots = []
    indexes = [0, 3, len(all_brs) - 1]
    for index in indexes:
        possible_lots.append(all_brs[index].previous_sibling.strip())

    text = "\n".join(possible_lots)
    return text


def get_data():
    url = "https://halkarz.com/"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    headers = {"User-Agent": user_agent}

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, "html.parser")

    halka_arz_list_li_elems = soup.find("ul", {"class": "halka-arz-list"}).find_all("li")
    today = get_local_datetime()
    actives = []
    for elem in halka_arz_list_li_elems:
        co_li = elem.find("h3", {"class": "il-halka-arz-sirket"})
        detail_page_url = co_li.find("a")["href"]
        a_elem = co_li.find("a")
        company = a_elem.text
        bist_code = elem.find("span", {"class": "il-bist-kod"}).text.strip()
        link = a_elem["href"]
        dates = elem.find("span", {"class": "il-halka-arz-tarihi"}).find("time").text.replace(" - ", ", ")
        if dates == "Hazırlanıyor...":
            continue

        splitted_dates = dates.split(",")
        last_date = splitted_dates[-1]
        year = last_date.split(" ")[-1]
        for dates in dates.split(","):
            dates = dates.strip()
            parsed_days = dates.split(" ")[0].split("-")
            month = dates.split(" ")[1]
            month = MONTHS[month.title()]
            year = dates.split(" ")[2] if len(dates.split(" ")) > 2 else year
            for day in parsed_days[::-1]:
                datetime_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                if check_dates_are_same(today, datetime_obj):
                    detail_page = requests.get(detail_page_url)
                    detail_soup = BeautifulSoup(detail_page.content, "html.parser")
                    arz_time_range = time_range(detail_soup)
                    price = get_price(detail_soup)
                    possible_lots = get_possible_lots(detail_soup)
                    actives.append({"company": company, "link": link, "dates": dates, "bist_code": bist_code,
                                    "time_range": arz_time_range, "price": price, "possible_lots": possible_lots})

                if (
                        (datetime_obj.day < today.day and day == parsed_days[
                            0]) or datetime_obj.month < today.month or datetime_obj.year < today.year):
                    return actives

    return actives


def send_notification_to_all(message, notification_classes):
    for notification_class in notification_classes:
        notification_class().send_notification(message)


def check_halka_arz_and_prepare_message():
    actives = get_data()
    message = "Bugün halka arzı olan şirketler:\n\n"
    for index, company in enumerate(actives):
        message += (f"{NUMBER_EMOJIS[index]} {company['bist_code']} - {company['company']}\n"
                    f"- {company['dates']} - {company['time_range']}\n"
                    f"- {company['price']}\n"
                    f"{company['possible_lots']}\n")

    if actives:
        return message
