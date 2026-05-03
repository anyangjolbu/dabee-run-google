import datetime

_live_logs = []

def add_log(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} [INFO] main — {msg}"
    print(log_entry)
    _live_logs.append(log_entry)
    if len(_live_logs) > 500:
        _live_logs.pop(0)

def get_live_logs():
    return _live_logs

def clear_logs():
    _live_logs.clear()
