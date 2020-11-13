from datetime import datetime


def log(message):
    print("[" + datetime.now().strftime("%H:%M:%S") + "]: " + message)
