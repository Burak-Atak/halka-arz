import azure.functions as func
from notifications import *

app = func.FunctionApp()
telegram_app = None


@app.schedule(schedule="0 0 0 1 * *", arg_name="init", use_monitor=True, run_on_startup=True)
async def init(init: func.TimerRequest) -> None:
    global telegram_app
    telegram_app = TelegramNotification().app
    await telegram_app.initialize()


@app.function_name(name="myTimer")
@app.schedule(schedule=SETTINGS["SCHEDULE_CONFIG"], arg_name="myTimer", use_monitor=True)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    try:
        message = check_halka_arz_and_prepare_message()
        if message:
            send_notification_to_all(message, notification_classes)

    except Exception as e:
        logging.error(e)


@app.route(route="telegram", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    global telegram_app
    try:
        if not telegram_app:
            telegram_app = TelegramNotification().app
            await telegram_app.initialize()
            logging.warning("Telegram app initialized.")
        req = req.get_json()
        update = Update.de_json(req, telegram_app.bot)
        await telegram_app.process_update(update)
        return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        logging.error(e)
        return func.HttpResponse("Internal Server Error", status_code=500)


@app.route(route="send_all", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def send_all(req: func.HttpRequest) -> func.HttpResponse:
    try:
        message = check_halka_arz_and_prepare_message()
        if message:
            send_notification_to_all(message, notification_classes)
        return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        logging.error(e)
