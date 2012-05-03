import datetime
 
def time_to_string(tm):
    return tm.strftime('%I:%M %p')

def time_serialize(tm):
    return tm.strftime('%H:%M')

def time_add_mins(tm, mins):
    fulldate = datetime.datetime(1,1,1,tm.hour,tm.minute,tm.second)
    fulldate = fulldate + datetime.timedelta(minutes = mins)
    return fulldate.time()