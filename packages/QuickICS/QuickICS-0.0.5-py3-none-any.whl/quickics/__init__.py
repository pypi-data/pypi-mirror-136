from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
import csv
import os


class Ics():

    rem_text = '*** Reminder ***\n\nIn your .csv file on your Desktop\n\n\
02/06/2022,16:00:00,1:30,Anchor Avon Lake OH 44012\n\n'
    ical = []
    events = []

    def __init__(self):
        self.csv_file = input(f'{Ics.rem_text}Type .csv filename:')
        self.event_title = input('Events title:')
        self.today_ = datetime.strftime(datetime.now(), '%d_%b_%y')
        self.csv_file = os.path.abspath(os.path.join(
                                        os.path.expanduser("~/Desktop"),
                                        self.csv_file))
        self.save_as = os.path.abspath(os.path.join(
                                        os.path.expanduser("~/Desktop"), 
                                        f'{self.event_title}_{self.today_}.ics')
                                       )
        self.csv_reader(self.csv_file)
        self.create_calendar()

    def duration(self, time_):
        self.t = time_.split(":")
        self.h = self.t[0]
        self.m = self.t[1]
        self.dur_ = timedelta(hours=int(self.h), minutes=int(self.m))
        return self.dur_

    def csv_reader(self, file):
        self.file = self.csv_file
        with open(self.file) as f:
            r = csv.reader(f)
            for i in r:
                if i != []:
                    self.date_time = f'{i[0]} {i[1]}'
                    self.dtstamp = datetime.strptime(self.date_time, 
                                                     '%m/%d/%Y %H:%M:%S')
                    self.duration_ = self.duration(i[2])
                    self.location = vText(i[3])
                    Ics.ical.append((
                            self.event_title,
                            self.dtstamp,
                            self.duration_,
                            self.location
                        ))

    def create_calendar(self):
        for x, i in enumerate(self.ical):
            event = Event()
            event.add("summary", i[0])
            event.add("dtstamp", i[1])
            event.add("dtstart", i[1])
            event.add("dtend", i[1] + i[2])
            event.add("location", i[3])
            Ics.events.append(event)
        cal = Calendar()
        cal.add('prodid', '-//Michael H. Roberts//Sports//')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        for evnt in Ics.events:
            cal.add_component(evnt)
        with open(self.save_as, 'wb') as f:
            f.write(cal.to_ical())


if __name__ == '__main__':
    Ics()
