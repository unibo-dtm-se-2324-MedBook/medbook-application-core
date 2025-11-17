from flet import *
from artefact.utils.traits import *
from artefact.utils.validation import Validator
from artefact.service.authentication import check_email

class FirstPage(Container):

    def __init__(self):
        super().__init__()
        self.expand = True         
        self.offset = transform.Offset(0,0,)

        self.validator = Validator()
        self.error_border = error_border

        self.title = Text(value = 'MedBook', weight = 'bold', size = 20, color = txt_color_wt)
        self.subtitle = Text('Health in a convenient format', weight = 'bold', size = helper_txt_size, color = txt_color_wt)
        
        self.text_enter_email = Text('Please enter your email', size = helper_txt_size, color = txt_color_wt, italic = True)
        self.email = TextField(
            hint_text = 'Email',
            hint_style = TextStyle(size = helper_txt_size, color = input_hint_color),
            text_style = TextStyle(size = helper_txt_size, color = input_hint_color),
            height = txf_height,
            bgcolor = 'white',
            border_radius = btn_txtfield_b_radius
        )
        
        self.btn_check_email = ElevatedButton(
            content = Text('Continue', size = general_txt_size, color = txt_color_wt),
            height = txf_height,
            width = btn_width,
            bgcolor = Dark_bgcolor,
            style = ButtonStyle(shape = RoundedRectangleBorder(radius = btn_txtfield_b_radius)),
            on_click = self.check_email
        )

    def build(self):
        self.first_content = Column(
            spacing = 8,
            controls = [
                Row(alignment = 'center', controls = [self.title]),
                self.subtitle,

                self.text_enter_email,
                self.email,
                Container(height = 1),

                self.btn_check_email,
                Container(height = 1),
        ])
        
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
                    padding = padding.only(top = 30, left = 10, right = 10, bottom = 10),
                    content= Column(controls=[
                        Container(height = 160),
                        Container(
                            padding = 10,
                            bgcolor = '#cc2d2b2c',
                            border_radius = 10,
                            content = self.first_content
                        )
                    ])
                ),
            ])
        )

        return self.content
    
    def check_email(self, e):
        if not self.validator.email_correctness(self.email.value):
            self.email.border_color = self.error_border
            self.email.update()
        else:
            email_input = self.email.value
            email_exist = check_email(email_input)
            if email_exist:
                self.page.session.set('email', self.email.value)
                self.page.go('/login_page')
            else:
                self.page.session.set('email', self.email.value)
                self.page.go('/signup_page')
            
