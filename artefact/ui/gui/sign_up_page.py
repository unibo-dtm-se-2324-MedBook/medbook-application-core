from flet import *
from artefact.utils.traits import *
from artefact.utils.validation import Validator
from artefact.service.authentication import create_user

class SignUpPage(Container):

    def __init__(self):
        super().__init__()
        self.expand = True
        self.offset = transform.Offset(0,0,)
        
        self.validator = Validator()
        self.error_border = error_border

        self.signup_title = Container(
            alignment = alignment.center,
            padding = padding.all(0),
            margin = margin.all(0),
            content = Text(
                value = 'Sign Up',
                weight = FontWeight.BOLD,
                size = general_txt_size,
                color = txt_color_wt,
                text_align = TextAlign.CENTER 
            )
        )

        self.text_welcome = Container(
            padding = padding.all(0),
            margin = margin.all(0),
            content = Column(
                spacing = 0,
                controls=[
                    Text("Seems you don't have account.", size = helper_txt_size, color = txt_color_wt),
                    Text("Let's get you signed up!", size = helper_txt_size, color = txt_color_wt),
                ]
            )
        )
        
        self.name = self.create_txtField('Name')
        self.surname = self.create_txtField('Surname')
        self.email =  self.create_txtField('Email') 
        
        self.text_password_rule = Container(
            padding = padding.all(0),
            margin = margin.all(0),
            content = Text('Use at least 8 characters, with 1 number and 1 special character',
                size = helper_txt_size,
                color = txt_color_wt,
                italic = True,
                no_wrap = False,
            ),
        )

        self.view_passw = Text(value = 'View', color = Dark_bgcolor)
        self.password = TextField(
            password = True,
            suffix = Container(
                on_click = self.show_hide_passw,
                content = self.view_passw),
            hint_text = 'Password',
            hint_style = TextStyle(size = helper_txt_size, color = input_hint_color),
            text_style = TextStyle( size = helper_txt_size, color = input_hint_color))

        self.text_policy = Column(
            spacing = 0,
            controls = [
                Text(value = 'By clicking button below,', size = helper_txt_size, color= txt_color_wt),
                Row(
                    spacing = 0,
                    controls = [
                        Text(value = 'I agree to', size = helper_txt_size, color= txt_color_wt),
                        Text(value = ' Terms of Privacy Policy', size = helper_txt_size, color='#FFFAFA', italic= True)
                    ]
                )
            ]
        )

        self.button_register = ElevatedButton(
            content = Text('Agree and Continue', size = general_txt_size, color = txt_color_wt),
            height = txf_height,
            width = btn_width,
            bgcolor = Dark_bgcolor,
            style = ButtonStyle(shape = RoundedRectangleBorder(radius = btn_txtfield_b_radius)),
            on_click = self.signup
        )
        
        self.content = None


    def build(self):  
        self.email.value = self.page.session.get('email')

        self.sighup_content = Column(
            spacing = 5,
            tight = True,
            controls = [
                self.signup_title,

                self.text_welcome,

                Container(
                    height=txf_height,
                    bgcolor='white',
                    border_radius=10,
                    content=self.name
                ),
                Container(
                    height=txf_height,
                    bgcolor='white',
                    border_radius=10,
                    content=self.surname
                ),
                Container(
                    height=txf_height,
                    bgcolor='white',
                    border_radius=10,
                    content=self.email,
                ),
                
                self.text_password_rule,

                Container(
                    height=txf_height,
                    bgcolor='white',
                    border_radius=10,
                    content=self.password
                ),

                self.text_policy,
                self.button_register,

                Container(height = 10)
            ]
        )
        
        self.content = Container(
            width = base_width,
            height = base_height,
            border_radius = b_radius,
            bgcolor = '#7b9faf',
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
                        Container(padding = padding.only(top=5, left=10, right=10, bottom=10), bgcolor = '#cc2d2b2c', border_radius = 10, content = self.sighup_content)
                    ])
                )
            ])
        )

        return self.content

    def create_txtField(self, hint_name):
        return TextField(
            hint_text = hint_name,
            hint_style = TextStyle(size = helper_txt_size, color = input_hint_color),
            text_style = TextStyle(size = helper_txt_size, color = input_hint_color),
            text_align = TextAlign.LEFT)

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


    def signup(self, e):
        if not self.validator.name_correctness(self.name.value):
            self.name.border_color = self.error_border
            self.name.update()
        if not self.validator.surname_correctness(self.surname.value):
            self.surname.border_color = self.error_border
            self.surname.update()
        if not self.validator.email_correctness(self.email.value):
            self.email.border_color = self.error_border
            self.email.update()
        if not self.validator.password_correctness(self.password.value):
            self.password.border_color = self.error_border
            self.password.update()
        else:
            name = self.name.value
            surname = self.surname.value
            email = self.email.value
            password = self.password.value

            create_user(name, surname, email, password)
            self.page.go('/login_page')
            