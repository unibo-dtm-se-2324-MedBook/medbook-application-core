from flet import *
import calendar
import datetime as dt
from artefact.utils.traits import *
from artefact.ui.gui.components.navigation import NavigationBar
from artefact.ui.gui.components.page_header import PageHeader
from artefact.service.database import save_pill_database, load_medicines_for_user, delete_pill_database
from firebase_admin import auth as firebase_auth
from artefact.service.notifications import NotificationService


class MainPage(UserControl):

    def __init__(self):
        super().__init__()
        self.expand = True
        self.offset = transform.Offset(0,0,)
        
        self.token = ''
        self.user_uid = ''

        # Visual for Calendar
        self.data_by_date = {}

        self.today = dt.datetime.today()
        self.year = self.today.year
        self.month = self.today.month

        self.prev_btn = IconButton(
            icons.ARROW_BACK, 
            icon_color = unit_color_dark, 
            icon_size = 16, 
            width = 32,
            height = 32,
            on_click = self.prev_month)
        self.next_btn = IconButton(
            icons.ARROW_FORWARD, 
            icon_color = unit_color_dark, 
            icon_size = 16, 
            width = 32,
            height = 32,
            on_click = self.next_month)
        
        ## Weekday headers
        weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        self.weekdays_row = Row(
            spacing = 0,
            controls = [
                Container(
                    width = calendar_width / 7,
                    height = 25,
                    alignment = alignment.center,
                    padding = padding.only(bottom = 3),
                    content = Text(day, size = calendar_txt, weight = FontWeight.BOLD),
                    border = border.only(
                        bottom = border.BorderSide(2, unit_color_dark)
                    )
                ) for day in weekdays
            ]
        )

        ## Container for the calendar with days
        self.calendar = Container(
            height = calendar_height,
            width = calendar_width,
            padding = padding.all(0),
            margin  = margin.all(0),
            content = Column(spacing = 0, tight = True, controls = [])
        )

        # Button to add new pill
        self.btn_add_pill = ElevatedButton(
            content = Text('Add the pill', size = 14, color = Colors.WHITE),
            height = txf_height,
            width = btn_width,
            bgcolor = Dark_bgcolor,
            style = ButtonStyle(shape = RoundedRectangleBorder(radius=10)),
            on_click = self.show_form
        )
        self.form = None 


    def build(self):
        # Import navigation
        page_header = PageHeader(current_page = None)
        
        self.month_header = Text(f'{calendar.month_name[self.month]} {self.year}', size = general_txt_size, italic = True)

        self.token = self.page.session.get('token')
        if self.token and not self.page.session.get('reminders_started'):
            notif_service = NotificationService(self.page, self.token, self.user_uid, page_header = page_header)
            self.page.overlay.append(notif_service)

        self.user_uid = self.page.session.get('uid')
        if self.token:
            # self.user_uid = firebase_auth.verify_id_token(self.token)['uid']
            self.data_by_date = load_medicines_for_user(self.user_uid, self.token, self.year, self.month)
            # print('After calling load_medicines_for_user', self.data_by_date)
        # else: print("token wasn't found")
        self._generate_calendar()


        # Combine visual elements of Schedule page
        schedule_content = Container(
            content = Column(
                spacing = 4,
                controls = [
                    page_header,
                    Row(alignment = MainAxisAlignment.CENTER,
                        controls = [Text('Schedule', weight = FontWeight.BOLD, size = 16)]),
                    Row(alignment = 'spaceBetween',
                        controls = [self.prev_btn, self.month_header, self.next_btn],
                    ),
                    Column(
                        spacing = 0,     
                        controls = [
                            self.weekdays_row,
                            self.calendar,
                        ]
                    ),
                    Container(
                        margin = padding.only(bottom = 20, top = 10),
                        content = self.btn_add_pill
                    )
                ]
            )
        )

        # Properties of Schedule page: basic and animation
        self.schedule = Row(
            alignment='end',
            controls=[Container(
                width = base_width, 
                height = base_height, 
                bgcolor = Light_bgcolor,
                border_radius = b_radius,
                animate = animation.Animation(600, AnimationCurve.DECELERATE),
                animate_scale = animation.Animation(400, curve = 'decelerate'),
                padding = padding.only(top = 15, left = 20, right = 40, bottom = 15),
                clip_behavior = ClipBehavior.ANTI_ALIAS,
                content = schedule_content
            )]
        )

        page_header.current_page = self.schedule

        # Import navigation
        navigation = NavigationBar(current_page = self.schedule)

        # Combine Navigation + Schedule
        self.content = Container(
            width = base_width, 
            height = base_height, 
            bgcolor = Light_bgcolor,
            border_radius = b_radius,
            expand = True,
            content = Stack(
                controls = [navigation, self.schedule]
            )
        )

        return self.content


    # Functions to go one month forward or back
    def prev_month(self, e):
        if self.month == 1:
            self.month, self.year = 12, self.year - 1
        else:
            self.month -= 1

        if self.token:
            self.data_by_date = load_medicines_for_user(self.user_uid, self.token, self.year, self.month)

        self.month_header.value = f'{calendar.month_name[self.month]} {self.year}'
        self._generate_calendar()
        self.update()

    def next_month(self, e):
        if self.month == 12:
            self.month, self.year = 1, self.year + 1
        else:
            self.month += 1
        
        if self.token:
            self.data_by_date = load_medicines_for_user(self.user_uid, self.token, self.year, self.month)

        self.month_header.value = f'{calendar.month_name[self.month]} {self.year}'
        self._generate_calendar()
        self.update()
    
    # Build the part of calendar with dates and markers
    def _generate_calendar(self):
        # print("Keys in data_by_date:", list(self.data_by_date.keys()))
        weeks = calendar.monthcalendar(self.year, self.month)
        rows = []
        row_height = calendar_height / 6
        cell_width = calendar_width  / 7

        for week in weeks:
            cells = []
            for day in week:
                date_key = f'{self.year}-{self.month:02d}-{day:02d}'
                pills = self.data_by_date.get(date_key, [])
                # print('date_key = ', date_key)
                # print('Pills = ', pills)
                
                markers = []
                corners = [
                    {"left": 4, "top": 2},
                    {"right": 4, "top": 2},
                    {"left": 4, "bottom": 2},
                ]

                for i in range(min(len(pills), 3)):
                    color = (Colors.BLUE_ACCENT_200, Colors.PURPLE_ACCENT_200, Colors.TEAL_ACCENT_200)[i]
                    markers.append(
                        Container(
                            width = 5,
                            height = 5,
                            bgcolor = color,
                            border_radius = 2,
                            **corners[i]
                        )
                    )
                if len(pills) > 3:
                    markers.append(
                        Container(
                            content = Text(f'+{len(pills) - 3}', size = 8, weight = FontWeight.BOLD),
                            right = 4,
                            bottom = 1
                        )
                    )

                date_container = Container(
                    content = Text(str(day) if day else '', size = calendar_txt),
                    alignment = alignment.center,
                    padding = padding.all(0),
                    margin = margin.all(0),
                )

                markers_container = Container(
                    expand = True,
                    padding = padding.all(0),
                    margin = margin.all(0),
                    content = Stack(
                        expand = True,
                        controls = markers
                    )
                )

                cell_content = Column(
                    spacing = 0, 
                    tight = True,
                    controls = [date_container, markers_container]
                )

                cells.append(
                    Container(
                        width = cell_width, 
                        height = row_height,
                        padding = padding.all(0),
                        margin = margin.all(0),
                        border = border.only(
                            bottom = border.BorderSide(1, unit_color_dark)
                        ),
                        content = cell_content,
                        on_click = (lambda e, d = day: self.open_day_dialog(d)) if pills else None
                    )
                )
            rows.append(Row(spacing = 0, tight = True, controls = cells))
        self.calendar.content.controls = rows


    # Method to open window with all medicines identified on chosen day
    def open_day_dialog(self, day):
        date_key = f'{self.year}-{self.month:02d}-{day:02d}'
        pills = self.data_by_date.get(date_key, [])

        list_view = ListView(
            expand = True,
            spacing = 10,
            padding = padding.all(0),
        )
        
        for pill in pills:
            list_view.controls.append(
                Container(
                    width = btn_width,
                    bgcolor = minor_light_bgcolor,
                    border = border.all(1, unit_color_dark),
                    border_radius = 10,
                    padding = padding.all(5),
                    margin = padding.all(0),
                    alignment = alignment.center,
                    content = Text(pill['medicine_name'], size = general_txt_size),
                    on_click = lambda e, p = pill: self._show_med_detail(date_key, p)
                )
            )

        med_list_dialog = AlertDialog(
            bgcolor = minor_light_bgcolor,
            inset_padding = padding.only(top = 20, left = 10, right = 10, bottom = 10),
            modal = True,

            title = Container(
                alignment = alignment.center,
                content = Text(f'{calendar.month_name[self.month]} {day:02d}', size = 18,) # weight = FontWeight.BOLD
            ),
            title_padding = padding.only(top = 20, bottom = 10),

            content_padding = padding.only(top = 0, left = 20, right = 20),
            content = Column(controls = [Divider(thickness = 2, color = unit_color_dark), list_view], spacing = 20),
            actions = [TextButton(
                content = Text('Close', size = general_txt_size, color = unit_color_dark), 
                on_click = lambda e: self._close_dialog()
            )]
        )
        self.page.dialog = med_list_dialog
        med_list_dialog.open = True
        self.page.update()

    # Function to close a Dialog of the page    
    def _close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    # Method to open window with description of chosed medicine
    def _show_med_detail(self, date_key, pill):
        med_desctiption = AlertDialog(
            bgcolor = minor_light_bgcolor,
            inset_padding = padding.only(top = 20, left = 10, right = 10, bottom = 10),

            title = Container(
                alignment = alignment.center,
                content = Text(pill['medicine_name'], size = 18)
            ),
            title_padding = padding.only(top = 20, bottom = 10),

            content_padding = padding.only(top = 0, bottom = 15, left = 20, right = 20),
            content = Column(
                tight = True,
                controls = [
                    Divider(thickness = 2, color = unit_color_dark),
                    Row(controls =[
                        Text('Quantity:', size = general_txt_size, weight = FontWeight.BOLD),
                        Text(f'{pill['quantity']}', size = general_txt_size),
                    ]),
                    Row(
                        vertical_alignment = CrossAxisAlignment.START,
                        controls =[
                            Text('Note:', size = general_txt_size, weight = FontWeight.BOLD),
                            Text(f'{pill['note']}', 
                                size = general_txt_size, 
                                no_wrap=False,
                                overflow="visible",
                                expand=True,
                            ),
                        ]
                    ),
                    Container(
                        alignment = alignment.center, 
                        margin = padding.only(top = 10),   
                        content = TextButton(
                            content=Text('Delete the medicine', size = general_txt_size, color = Colors.WHITE),
                            height = txf_height,
                            style = ButtonStyle(
                                shape = RoundedRectangleBorder(radius=10),
                                bgcolor = Dark_bgcolor,
                            ),
                            on_click = lambda e: self._delete_pill(date_key, pill)
                        )
                    )
                ], 
            ),

            actions = [TextButton(
                content = Text('Close', size = general_txt_size, color = unit_color_dark), 
                on_click = lambda _: self._close_dialog()),
            ]
        )
        self.page.dialog = med_desctiption
        med_desctiption.open = True
        self.page.update()

    def _delete_pill(self, date_key, pill):
        # uid = firebase_auth.verify_id_token(self.token)['uid']
        key = pill['key']

        removal = delete_pill_database(self.user_uid, self.token, key)

        # Remove the entry locally
        if removal and date_key in self.data_by_date:
            self.data_by_date[date_key] = [i for i in self.data_by_date[date_key] if i["key"] != key]
            
            if not self.data_by_date[date_key]:
                del self.data_by_date[date_key]

        # Close dialog with medicine description
        self.page.dialog.open = False
        self.page.update()

        # Rebuild the calendar and update the UI inside UserControl
        self._generate_calendar()
        self.update()


    # Creating the form for new medicine
    def show_form(self, e):
        def create_TextField():
            return TextField(
                text_style = TextStyle(size = 12, color = input_hint_color),
                text_align = TextAlign.LEFT,
                height = txf_height,
                bgcolor = Colors.WHITE,
                border_radius = 10,
                border_color = unit_color_dark,
                border_width = 1,
                focused_border_color = unit_color_dark,
                focused_border_width = 2
            )
        
        self.medname_field = create_TextField()
        self.qty_field = create_TextField()
        self.selected_date = Text(str(self.today.date()), size = 12, color = input_hint_color)
        self.note_field = create_TextField()

        self.form = AlertDialog(
            bgcolor = minor_light_bgcolor,
            inset_padding = padding.only(top = 20, left = 10, right = 10, bottom = 10),

            title = Container(
                alignment = alignment.center,
                content = Text('New Medicine', size = 18)
            ),
            title_padding = padding.only(top = 20, bottom = 10),
            
            content_padding = padding.only(top = 0, left = 20, right = 20, bottom = 10),
            content = Column(
                width = base_width,
                spacing = 7,
                controls = [ 
                    Divider(thickness = 2, color = unit_color_dark),
                    Text('Medication name:', size = general_txt_size),
                    self.medname_field,
                    Text('Quantity of pill:', size = general_txt_size),
                    self.qty_field,
                    Text('Date to take pills:', size = general_txt_size),
                    Container(
                        bgcolor = Colors.WHITE,            
                        padding = padding.only(left = 10),
                        border_radius = 10,
                        border = BorderSide(                       
                            color = unit_color_dark, 
                            width = 1
                        ),
                        content = Row(spacing = 0,
                            alignment = 'spaceBetween',
                            controls = [
                                self.selected_date,
                                IconButton(
                                    icon = Icons.CALENDAR_MONTH_SHARP, 
                                    icon_size = 20,
                                    icon_color = unit_color_dark, 
                                    highlight_color ='#FFFAFA',
                                    style = ButtonStyle(shape = RoundedRectangleBorder(radius = border_radius.only( 
                                        top_right = 10,
                                        bottom_right = 10))
                                    ),
                                    on_click=lambda e: self.page.open(
                                        DatePicker(
                                            first_date = dt.datetime(year = 2024, month = 10, day = 1),
                                            last_date = dt.datetime(year = 2026, month = 10, day = 1),
                                            on_change = self.handle_change,
                                            on_dismiss = self.handle_dismissal,
                                        )
                                    )

                                )
                            ]
                        )
                    ),
                    Text('Note:', size = general_txt_size),
                    self.note_field
                ], 
            ),
            actions_padding = padding.only(top = 0, bottom = 15, left = 20, right = 20),
            actions = [
                Row(alignment = MainAxisAlignment.END,
                    controls = [    
                        TextButton(
                            content=Text('Cancel', size = general_txt_size, color = Colors.WHITE),
                            height = txf_height,
                            style = ButtonStyle(
                                shape = RoundedRectangleBorder(radius=10),
                                bgcolor = Dark_bgcolor,
                            ),
                            on_click = lambda _: self._close_dialog()
                        ),
                        TextButton(
                            content=Text('Save', size = general_txt_size, color = Colors.WHITE),
                            height = txf_height,
                            style = ButtonStyle(
                                shape = RoundedRectangleBorder(radius=10),
                                bgcolor = Dark_bgcolor,
                            ),
                            on_click = lambda e: self.save_medicine()
                        )
                ])
            ],
            modal = True,
        )

        self.page.dialog = self.form
        self.form.open = True
        self.page.update()

    # Functions for DatePicker's working
    def handle_change(self, e):
        self.selected_date.value = e.control.value.strftime('%Y-%m-%d')
        self.page.update()

    def handle_dismissal(self, e):
        self.page.snack_bar = SnackBar(
            content=Text("DatePicker dismissed"),
            duration = 2000
        )
        self.page.snack_bar.open = True
        self.page.update()
        
    # Function to save new medicine in database and to show it in the calendar
    def save_medicine(self):
        pill_name = self.medname_field.value
        pill_qty = self.qty_field.value
        pill_date = self.selected_date.value
        pill_note = self.note_field.value

        if pill_name and pill_qty and pill_date:
            new_key = save_pill_database(self.user_uid, self.token, pill_name, pill_qty, pill_date, pill_note)

            self.form.open = False
            self.page.snack_bar = SnackBar(Text('Medicine saved'))
            self.page.snack_bar.open = True
            self.page.update()

            # Update local dictionary and generate the calendar with new medicine
            entry = {
                'key': new_key,
                'medicine_name': pill_name,
                'quantity': pill_qty,
                'note': pill_note
            }
            self.data_by_date.setdefault(pill_date, []).append(entry)
            self._generate_calendar()
            self.update()
        else:
            self.page.snack_bar = SnackBar(Text('Please, fill all fields'))
            self.page.snack_bar.open = True
            self.page.update()


            
        


