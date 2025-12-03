from flet import *
from artefact.utils.traits import *
from artefact.ui.gui.components.navigation import NavigationBar
from artefact.ui.gui.components.page_header import PageHeader
from artefact.service.notifications import NotificationService
from firebase_admin import auth as firebase_auth
from artefact.utils.validation import Validator
from artefact.service.authentication import change_user_info

class SettingsPage(UserControl):
    
    def __init__(self):
        super().__init__()
        self.expand = True
        self.offset = transform.Offset(0,0,)

        self.validator = Validator()

        self.token = ''
        self.user_uid = ''
        self.user_name = ''
        self.user_surname = ''
        self.user_email = ''
        self.password = ''

        self.text_user_name = Text(size = 12)
        self.text_user_surname = Text(size = 12)
        self.text_user_email = Text(size = 12)

        # Button to edit user info
        self.btn_edit_info = ElevatedButton(
            content = Text('Edit information', size = 14, color = Colors.WHITE),
            height = txf_height,
            width = btn_width,
            bgcolor = Dark_bgcolor,
            style = ButtonStyle(shape = RoundedRectangleBorder(radius=10)),
            on_click = lambda _: self.edit_info_btn()
        )

    def build(self):
        page_header = PageHeader(current_page = None)
        
        self.user_uid = self.page.session.get('uid')
        self.token = self.page.session.get('token')
        
        # Check the timer to start notification service only once
        if self.token and not self.page.session.get('reminders_started'):
            notif_service = NotificationService(self.page, self.token, page_header = page_header)
            self.page.overlay.append(notif_service)
 
        self.load_user_info()

        def create_row_info(name_info, text_control):
            return Row(alignment = MainAxisAlignment.START, 
                controls = [
                    Text(name_info, size = general_txt_size, weight = FontWeight),
                    Container(
                        expand = True,
                        padding = padding.all(5),
                        border_radius = 10,
                        border = border.all(color = unit_color_dark, width = 1),
                        content = text_control
                    )
                ]
            )
        row_user_name = create_row_info('Name:', self.text_user_name)
        row_user_surname = create_row_info('Last name:', self.text_user_surname)
        row_user_email = create_row_info('Email:', self.text_user_email)


        settings_content = Container(
            content = Column(
                spacing = 4,
                controls = [
                    page_header,
                    Row(alignment = MainAxisAlignment.CENTER,
                        controls = [Text('Personal info', weight = FontWeight.BOLD, size = 16)]
                    ),
                    Container(
                        expand = True,
                        padding = padding.only(top = 10, bottom = 20),
                        content = Column(
                            spacing = 10,
                            controls = [
                                row_user_name,
                                row_user_surname,
                                row_user_email,
                            ]
                        )
                    ),
                    Container(
                        margin = padding.only(bottom = 15, top = 10), # b 20
                        content = self.btn_edit_info
                    )
                ]
            )
        )

        # Properties of Schedule page: basic and animation
        self.settings = Row(
            alignment='end',
            controls=[Container(
                width = base_width, 
                height = base_height, 
                bgcolor = Light_bgcolor,
                border_radius = b_radius,
                animate = animation.Animation(600, AnimationCurve.DECELERATE),
                animate_scale = animation.Animation(400, curve = 'decelerate'),
                padding = padding.only(top = 15, left = 20, right = 40, bottom = 5), # 15
                clip_behavior = ClipBehavior.ANTI_ALIAS,
                content = settings_content
            )]
        )
        
        page_header.current_page = self.settings
        navigation = NavigationBar(current_page = self.settings)

        # Combine Navigation + Schedule
        self.content = Container(
            width = base_width, 
            height = base_height, 
            bgcolor = Light_bgcolor,
            border_radius = b_radius,
            expand = True,
            content = Stack(
                controls = [navigation, self.settings]
            )
        )

        return self.content

    # Open navigation moving the settings to the right
    def shrink(self, e):
        self.settings.controls[0].width = 70
        self.settings.controls[0].scale = transform.Scale(1, alignment=alignment.center_right)
        self.settings.controls[0].border_radius = border_radius.only(top_left=35, top_right=0, bottom_left=35, bottom_right=0)
        self.settings.update()

    def load_user_info(self):
        user = firebase_auth.get_user(self.user_uid)
    
        full_name = user.display_name or ''
        if '_' in full_name:
            self.user_name, self.user_surname = full_name.split('_', 1)
        else:
            self.user_name, self.user_surname = full_name, ''
        
        self.user_email = user.email

        self.text_user_name.value = self.user_name
        self.text_user_surname.value = self.user_surname
        self.text_user_email.value = user.email

    def edit_info_btn(self):
        def create_row_edit_info(name_info, hint_name):
            txt_field = TextField(
                expand = True,

                hint_text = hint_name,
                hint_style = TextStyle(size = 12, color = input_hint_color),
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
            
            return Row(alignment = MainAxisAlignment.START, 
                controls = [
                    Text(name_info, size = general_txt_size, weight = FontWeight),
                    txt_field
                ]
            ), txt_field
        row_name, self.name_field = create_row_edit_info('Name:', self.user_name)
        row_surname, self.surname_field = create_row_edit_info('Last name:', self.user_surname)
        row_email, self.email_field = create_row_edit_info('Email:', self.user_email)

        edit_form = AlertDialog(
            bgcolor = minor_light_bgcolor,
            inset_padding = padding.only(top = 20, left = 10, right = 10, bottom = 10),

            title = Container(
                alignment = alignment.center,
                content = Text('Edit personal info', size = 18,)
            ),
            title_padding = padding.only(top = 20, bottom = 10),

            content_padding = padding.only(top = 0, left = 20, right = 20, bottom = 10),
            content = Column(
                width = base_width,
                spacing = 10,
                controls = [ 
                    Divider(thickness = 2, color = unit_color_dark),
                    Container(
                        expand = True,
                        padding = padding.all(0),
                        margin = padding.all(0),
                        content = Column(
                            spacing = 10,
                            controls = [
                                row_name,
                                row_surname,
                                row_email
                            ]
                        )
                    ),
                    TextButton(
                        content = Text('Save changes', size = general_txt_size, color = Colors.WHITE),
                        height = txf_height,
                        width = btn_width,
                        style = ButtonStyle(
                            shape = RoundedRectangleBorder(radius=10),
                            bgcolor = Dark_bgcolor,
                        ),
                        on_click = lambda e: self._save_changes()
                    )
                ], 
            ),

            actions_padding = padding.only(top = 0, bottom = 15, left = 20, right = 20),
            actions = [TextButton(
                content = Text('Cancel', size = general_txt_size, color = unit_color_dark), 
                on_click = lambda _: self._close_dialog()),
            ],

            modal = True,
        )

        self.page.dialog = edit_form
        edit_form.open = True
        self.page.update()

    def _close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _save_changes(self):
        error_border = 'red'
        if self.name_field.value != '' and not self.validator.name_correctness(self.name_field.value):
            self.name_field.border_color = error_border
            self.name_field.update()
        if self.surname_field.value != '' and not self.validator.surname_correctness(self.surname_field.value):
            self.surname_field.border_color = error_border
            self.surname_field.update()
        if self.email_field.value != '' and not self.validator.email_correctness(self.email_field.value):
            self.email_field.border_color = error_border
            self.email_field.update()
        else:
            if self.name_field.value != '': name = self.name_field.value
            else: name = self.user_name
            if self.surname_field.value != '': surname = self.surname_field.value
            else: surname = self.user_surname
            if self.email_field.value != '': email = self.email_field.value
            else: email = self.user_email

            change_user_info(name, surname, email, self.user_uid, self.page)

            self.load_user_info()
            self._close_dialog()
            
            self.update()
            

