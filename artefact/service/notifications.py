from flet import *
import asyncio
import datetime as dt
import calendar
from artefact.service.database import load_medicines_for_user
from firebase_admin import auth as firebase_auth


class NotificationService(UserControl):
    def __init__(self, page, token, uid, page_header):
        super().__init__()
        self.page = page
        self.token = token
        self.user_uid = uid
        
        self.page_header = page_header


    # did_mount is a life-cycle hook of the UserControl.
    # It is called automatically by the Flet engine after your control is first built and added to the page (i.e. after build() and the actual rendering)
    def did_mount(self):
        if not self.page.session.get('reminders_started'):
            self.page.session.set('reminders_started', True)
            # print('did_mount has run')
            self.page.run_task(self._schedule_daily_reminders)
    
    async def _schedule_daily_reminders(self):
        while True:
            now = dt.datetime.now()
            next_run = now.replace(hour = 6, minute = 0, second = 0, microsecond = 0)
            if now >= next_run:
                next_run += dt.timedelta(days = 1)
            
            delay_secs = (next_run - now).total_seconds()
            await asyncio.sleep(delay_secs)
            self._handle_daily_reminder()

    # Method will be called when the daily reminder is triggered
    def _handle_daily_reminder(self):
        today = dt.date.today().strftime('%Y-%m-%d')
        day = dt.date.today().day
        month = calendar.month_name[dt.date.today().month]
        
        pills = load_medicines_for_user(self.user_uid, self.token, dt.date.today().year, dt.date.today().month).get(today, [])
        if not pills:
            return
        self.page_header.notifications.clear()

        for p in pills:
            self.page_header.notifications.append({
                'date': f'{day:02d} {month}',
                'medicine_name': p['medicine_name']
            })

        self.page_header.set_unread(True)
