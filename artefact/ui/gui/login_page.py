from flet import *
from artefact.utils.traits import *
from artefact.utils.validation import Validator
from artefact.service.authentication import login_user, store_token
from firebase_admin import auth as firebase_auth

class LoginPage(Container):

    def __init__(self):
        super().__init__()
        self.expand = True
        self.offset = transform.Offset(0,0,)

        self.validator = Validator()
        self.error_border = 'red'

        self.email = ''
        self.text_email = Text(size = 12, color = 'white')

        self.view_passw = None
        self.password = None
        self.login_content = None
        self.content = None
    
    def build(self):
        self.email = self.page.session.get('email')
        self.text_email.value = f'Email: {self.email}'

        self.view_passw = Text(value= 'View', color = Dark_bgcolor)
        self.password = TextField(
            password = True,
            suffix=Container(
                on_click= self.show_hide_passw,
                content= self.view_passw),
            hint_text = 'Password',
            hint_style = TextStyle(size = 12, color = input_hint_color),
            text_style = TextStyle( size = 12, color = input_hint_color))
        
        self.login_content = Column(controls = [
            Row(alignment='center', controls = [Text(value= 'Login', weight='bold',size = 15, color='white')]),
            Column(
                spacing = 0,
                controls=[
                    Text(value= 'Nice to see you again!', weight='bold', size = 12, color='white'),
                    self.text_email
                ]
            ),
            Container(
                height=txf_height,
                bgcolor='white',
                border_radius=10,
                content=self.password
            ),
            
            Container(
                height = txf_height,
                width = btn_width,
                bgcolor= Dark_bgcolor,
                border_radius = 10,
                alignment= alignment.center,
                content= Text(value='Continue', size = 14, color='white'),
                # on_click= lambda _: self.page.go('/main_page')
                on_click = self.continuing
            ),
            Container(height = 3),
            Container(
                content = Row(alignment='center', controls = [Text(value="Forgot your password?", color = 'white', size = 12)]),
                on_click= lambda _: self.page.go('/passw_page')
            )
        ])
        
        self.content = Container(
            width = base_width,
            height = base_height,
            border_radius = b_radius,
            bgcolor = "#7b9faf",
            clip_behavior = ClipBehavior.ANTI_ALIAS,
            expand = True,
            content = Stack(controls = [
                Container(
                    width = base_width,
                    height = base_height,
                    top = -70,
                    content = Image(src='artefact/assets/images/first_page_ava2.jpg', scale = 1.1)
                ),
                Container(
                    width = base_width,
                    height = base_height,
                    padding = padding.only(top = 20, left = 10, right = 10),
                    content= Column(controls=[
                        Container(
                            data = 'first_page', 
                            height = 30, 
                            content = IconButton(
                                icon=Icons.KEYBOARD_RETURN, 
                                icon_size=17, 
                                icon_color='white', 
                                bgcolor=Dark_bgcolor, 
                                highlight_color ='#FFFAFA',
                                on_click= lambda _: self.page.go('/first_page')
                            ),
                        ),
                        Container(height=100),
                        Container(
                            padding = 10,
                            bgcolor = '#cc2d2b2c',
                            border_radius = 10,
                            content = self.login_content
                        )
                    ])
                )
            ])
        )

    def show_hide_passw(self, e):
        status = self.password.password
        if status == True:
            self.password.password = False
            self.view_passw.value = 'Hide'
        else: 
            self.password.password = True
            self.view_passw.value = 'View'
        self.password.update()
        self.view_passw.update()
    
    def continuing(self, e):
        if not self.validator.password_correctness(self.password.value):
            self.password.border_color = self.error_border
            self.password.update()
        else:
            email = self.email
            password = self.password.value

            self.page.splash = ProgressBar()
            self.page.update()

            token = login_user(email, password)
            self.page.session.set('token', token)

            self.page.splash = None
            self.page.update()

            if token:
                store_token(token)
                uid = firebase_auth.verify_id_token(token)['uid'] 
                self.page.session.set('uid', uid)
                self.page.go('/main_page')
            else:
                self.page.snack_bar = SnackBar(Text('Invalid password'))
                self.page.snack_bar.open = True
                self.page.update()

    