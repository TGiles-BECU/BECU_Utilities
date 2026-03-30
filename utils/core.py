from datetime import datetime, timedelta

def ymd(days=0, return_list=0):
    # returns date like 20260101
    selected_date = (datetime.now() + timedelta(days=days)).strftime("%Y%m%d")
    if not return_list:
        return selected_date
    else:
        return [
            selected_date[:4],
            selected_date[4:6],
            selected_date[6:],
        ]