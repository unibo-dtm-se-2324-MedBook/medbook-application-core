from flet import *
from artefact.utils.traits import *

class PageHeader(UserControl):
    def __init__(self, current_page):
        super().__init__()
        
        self.current_page = current_page

        self.btn_menu = IconButton(
            icon = icons.MENU,
            icon_size = 25,
            width = 30,
            height = 30,
            padding = padding.all(0),
            icon_color = Colors.BLACK,
            highlight_color ='#FFFAFA',
            on_click = self.shrink
        )

        # Notification settings
        self.unread_notif = False
        self.notifications = []

        self.btn_notification = IconButton(
            icon = icons.NOTIFICATIONS_OUTLINED,
            icon_size = 25,
            width = 30,
            height = 30,
            padding = padding.all(0),
            alignment = alignment.center,
            icon_color = Colors.BLACK,
            highlight_color ='#FFFAFA',
            on_click = lambda _: self.open_notifications_dialog()
        )

        # Tests with notification dialog
        # day = dt.datetime.today().day
        # month = calendar.month_name[dt.datetime.today().month]
        # self.notifications.append({"date": f"{day:02d} {month}", "medicine_name": "Test Pill"})
        # self.notifications.append({"date": f"{day:02d} {month}", "medicine_name": "Test Pill2"})
        # self.notifications.append({"date": f"{day:02d} {month}", "medicine_name": "Test Pill3"})
        # self.notifications.append({"date": f"{day:02d} {month}", "medicine_name": "Test Pill4"})

    def build(self):
        return Column(
            spacing = 4,
            controls = [
                Row(
                    alignment = 'spaceBetween',
                    controls = [
                        self.btn_menu,
                        Text(value = 'MedBook',  color = 'black'),
                        self.btn_notification
                    ]
                ),
                Divider()
            ]
        )
    
    # Open navigation moving the current page to the right
    def shrink(self, e):
        self.current_page.controls[0].width = 70
        self.current_page.controls[0].scale = transform.Scale(1, alignment=alignment.center_right)
        self.current_page.controls[0].border_radius = border_radius.only(top_left=35, top_right=0, bottom_left=35, bottom_right=0)
        self.current_page.update()

    # Method to open window with notifications
    def open_notifications_dialog(self):
        notifs = [
            Container(
                content = Column(
                    spacing = 0,
                    controls = [
                        Text(f'Today {n['date']}:', size = general_txt_size),
                        Text(f"don't forget to take {n['medicine_name']}", size = general_txt_size),
                    ]
                ),
                padding = padding.symmetric(vertical = 4, horizontal = 12),
                border = border.all(1, unit_color_dark),
                border_radius = 10
            )
            for n in self.notifications
        ]
        
        notif_dialog = AlertDialog(
            bgcolor = minor_light_bgcolor,
            inset_padding = padding.only(top = 20, left = 10, right = 10, bottom = 10),

            title = Text("Notifications", size = 18, text_align = 'center'),
            title_padding = padding.only(top = 20, bottom = 10),

            content_padding = padding.only(top = 0, left = 20, right = 20),
            content = Column(
                spacing = 10,
                controls = [
                    Divider(thickness = 2, color = unit_color_dark),
                    ListView(
                        expand = True,
                        spacing = 10,
                        padding = padding.only(top = 0, bottom = 10), 
                        controls = notifs)
                ]
            ),

            actions = [TextButton(
                content = Text('Close', size = general_txt_size, color = unit_color_dark), 
                on_click = lambda e: self.close_notif_dialog()
            )]
        )
        
        self.unread_notif = False
        self.btn_notification.icon_color = Colors.BLACK

        self.page.dialog = notif_dialog
        notif_dialog.open = True
        self.page.update()
        self.update()


    def close_notif_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    # Method to control if notifications were read or not
    def set_unread(self, has_unread: bool):
        self.unread_notif = has_unread
        self.btn_notification.icon_color = Colors.RED_900 if has_unread else Colors.BLACK
        self.update()