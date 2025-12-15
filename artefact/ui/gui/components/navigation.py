from flet import *
from artefact.utils.traits import *
from artefact.service.authentication import log_out

class NavigationBar(UserControl):
    def __init__(self, current_page):
        super().__init__()
        
        self.current_page = current_page

        self.btn_return = Row(
            spacing = 0,
            controls = [IconButton(
                icon = Icons.KEYBOARD_RETURN, icon_color = 'white', 
                on_click = self.restore, 
                icon_size = 20, 
                highlight_color = '#FFFAFA')
            ],
        )

        self.navig_title = Container(
            padding = padding.only(left = 15),
            content = Text('Your portable\nmedical card', size = 15, weight = 'bold', color = 'white')
        )

        self.btn_to_shedule_page = Row(controls = [
            TextButton(
                on_click = lambda e: self.page.route == '/main_page' and self.restore(e) or self.page.go('/main_page'),
                content = Row(controls = [
                    Icon(icons.SCHEDULE, color = "white60"),
                    Text(value = "Schedule",
                        size = 15,
                        weight = FontWeight.W_300,
                        color = "white",
                        font_family = "poppins"
                    )
                ])
            )
        ])
        
        self.btn_to_documents_page = Row(controls=[
            TextButton(
                on_click = lambda e: self.page.route == '/documents_page' and self.restore(e) or self.page.go('/documents_page'),
                content = Row(controls = [
                    Icon(icons.EDIT_DOCUMENT, color="white60"),
                    Text("Documents",
                        size=15,
                        weight=FontWeight.W_300,
                        color="white",
                        font_family="poppins"
                    )
                ])
            )
        ])

        self.btn_check_pill = Row(controls=[
            TextButton(
                on_click = lambda e: self.page.route == '/pill_check_page' and self.restore(e) or self.page.go('/pill_check_page'),
                content = Row(controls = [
                    Icon(icons.DOCUMENT_SCANNER, color="white60"),
                    Text("Check",
                        size=15,
                        weight=FontWeight.W_300,
                        color="white",
                        font_family="poppins"
                    )
                ])
            )
        ])

        self.btn_user_settings_page = Row(controls=[
            TextButton(
                on_click = lambda e: self.page.route == '/settings_page' and self.restore(e) or self.page.go('/settings_page'),
                content = Row(controls = [
                    Icon(icons.PERSON_OUTLINE, color="white60"),
                    Text(value="Personal info",
                        size = 15,
                        weight = FontWeight.W_300,
                        color = "white",
                        font_family = "poppins"
                    )
                ])
            )
        ])

        self.btn_exit = Row(controls=[
            TextButton(
                content = Row(controls = [
                    Icon(icons.EXIT_TO_APP, color="white60"),
                    Text("Exit",
                        size = 15,
                        weight = FontWeight.W_300,
                        color = "white",
                        font_family = "poppins"
                    ) 
                ]),
                on_click = self.exit
            )
        ])
        

    def build(self):
        return Container(
            bgcolor = Dark_bgcolor,
            border_radius = b_radius,
            padding = padding.only(top = 10, left = 8, bottom = 5),
            content = Column(controls = [
                self.btn_return,
                self.navig_title,
                Container(height = 10),
                self.btn_to_shedule_page,
                Container(height = 5),
                self.btn_to_documents_page,                            
                Container(height = 5),
                self.btn_check_pill, 
                Container(height = 5),
                self.btn_user_settings_page,
                Container(height = 20),
                self.btn_exit
            ])
        )

    # Close navigation bar opening a current page
    def restore(self, e):
        self.current_page.controls[0].width = base_width
        self.current_page.controls[0].border_radius = b_radius
        self.current_page.controls[0].scale = transform.Scale(1, alignment = alignment.center_right)
        self.current_page.update()
        
    # Function of exit clicking the 'Exit' button in navigation
    def exit(self, e):
        token = self.page.session.get('token')
        print('Token is gotten')
        if token: 
            log_out(token)
            self.page.session.clear()
            self.page.go('/first_page')
        else:
            self.page.snack_bar = SnackBar(Text('Something is wrong, try again'))
            self.page.snack_bar.open = True
            self.page.update() 