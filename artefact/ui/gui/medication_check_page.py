from flet import *
from artefact.utils.traits import *
from artefact.ui.gui.components.navigation import NavigationBar
from artefact.ui.gui.components.page_header import PageHeader
from artefact.service.notifications import NotificationService
from artefact.utils.validation import Validator
from artefact.utils.constants import SEX_OPTIONS, COUNTRY_OPTIONS
from artefact.service.api_openfda_service import PatientFilters, fetch_risks
from flet import PieChart, PieChartSection

class MedicineCheckPage(UserControl):
    
    def __init__(self):
        super().__init__()
        self.expand = True
        self.offset = transform.Offset(0,0,)

        self.validator = Validator()
        self.error_border = 'red'

        self.token = ''

        # Enter filters area
        self.title = Row(
            alignment = MainAxisAlignment.CENTER,
            controls = [Text('MedCheck', weight = FontWeight.BOLD, size = title_txt_size)]
        )
        self.page_description = Text('Here you can check possible side effects of the medicine', 
            size = helper_txt_size, text_align = TextAlign.JUSTIFY)
        self.txt_details = Container(
            padding = padding.only(top = 5, bottom = 5), # italic = True
            content = Text('Please, enter your details', size = general_txt_size)
        )

        # Button to search for risks
        self.btn_search_risks = ElevatedButton(
            content = Text('Search for risks', size = general_txt_size, color = Colors.WHITE),
            height = txf_height,
            width = btn_width,
            bgcolor = Dark_bgcolor,
            style = ButtonStyle(shape = RoundedRectangleBorder(radius=10)),
            on_click = lambda _: self.search_risks()
        )

        # Results area
        self.results_chart_holder = Container(
            expand = True,
            alignment = alignment.center, 
            padding = padding.symmetric(vertical = 0)
        )
        self.results_anchor = Container(height = 1, key = 'results_anchor')
        self.results_section = Column(spacing = 4, controls = [])
    
    def build(self):
        page_header = PageHeader(current_page = None)
        
        self.token = self.page.session.get('token')

        # Check the timer to start notification service only once
        if self.token and not self.page.session.get('reminders_started'):
            notif_service = NotificationService(self.page, self.token, page_header = page_header)
            self.page.overlay.append(notif_service)

        row_drug, self.user_drug = self._create_txtfield_info('Drug:', 'Ibuprofen')
        row_age, self.user_age = self._create_txtfield_info('Age (years):', '26')

        row_sex, self.user_sex, self.container_user_sex = self._create_dropdown_info('Gender:', SEX_OPTIONS)
        row_country, self.user_country, self.container_user_country = self._create_dropdown_info('Country:', COUNTRY_OPTIONS)

        self.check_content = ListView(
            expand = True,
            spacing = 4,
            padding = padding.only(top = 0, bottom = 20, right = 40, left = 20),
            controls = [
                self.title,
                self.page_description,
                self.txt_details,
                Container(
                    expand = True,
                    padding = padding.only(top = 5),
                    content = Column(
                        spacing = 10,
                        controls = [
                            row_drug,
                            row_sex,
                            row_age, 
                            row_country
                        ]
                    )
                ),
                Container(
                    margin = padding.only(top = 15),
                    content = self.btn_search_risks
                ),
                self.results_anchor,
                self.results_section
            ])

        page_content = Container(
            content = Column(
                spacing = 4,
                controls = [
                    Container(
                        content = page_header,
                        padding = padding.only(left = 20, right = 40, top = 15)
                    ), 
                    self.check_content]
            )
        )

        # Properties of Medicines check page: basic and animation
        self.medicine_check = Row(
            alignment='end',
            controls=[Container(
                width = base_width, 
                height = base_height, 
                bgcolor = Light_bgcolor,
                border_radius = b_radius,
                animate = animation.Animation(600, AnimationCurve.DECELERATE),
                animate_scale = animation.Animation(400, curve = 'decelerate'),
                # padding = padding.only(top = 15, left = 20, right = 40, bottom = 5), # 15
                clip_behavior = ClipBehavior.ANTI_ALIAS,
                content = page_content
            )]
        )
        
        page_header.current_page = self.medicine_check
        navigation = NavigationBar(current_page = self.medicine_check)

        # Combine Navigation + Medicines check page
        self.content = Container(
            width = base_width, 
            height = base_height, 
            bgcolor = Light_bgcolor,
            border_radius = b_radius,
            expand = True,
            content = Stack(
                controls = [navigation, self.medicine_check]
            )
        )

        return self.content
    

    # Open navigation moving the medicine check to the right
    def shrink(self, e):
        self.settings.controls[0].width = 70
        self.settings.controls[0].scale = transform.Scale(1, alignment=alignment.center_right)
        self.settings.controls[0].border_radius = border_radius.only(top_left=35, top_right=0, bottom_left=35, bottom_right=0)
        self.settings.update()

    # Creating TextField with common design for maintaining user information
    def _create_txtfield_info(self, name_info, hint_name):
        def _on_change(e, tf = None):
            if tf and isinstance(tf.value, str) and tf.value.strip():
                tf.border_color = unit_color_dark
                tf.update()    
            
        txt_field = TextField(
            expand = True,

            hint_text = hint_name,
            hint_style = TextStyle(size = helper_txt_size, color = input_hint_color),
            text_style = TextStyle(size = helper_txt_size, color = input_hint_color),
            text_align = TextAlign.LEFT,

            height = txf_height,
            bgcolor = Colors.WHITE,
            border_radius = 10,
            border_color = unit_color_dark,
            border_width = 1,
            focused_border_color = unit_color_dark,
            focused_border_width = 2,
            on_change = lambda e: _on_change(e, tf = txt_field)
        )
        
        return Row(alignment = MainAxisAlignment.START, 
            controls = [
                Text(name_info, size = general_txt_size, weight = FontWeight),
                txt_field
            ]
        ), txt_field
    
    # Creating Dropdown with common design for maintaining user information
    def _create_dropdown_info(self, name_info, from_list_name):
        def _on_dd_change(e, dd = None, wrapper = None):
            if dd.value not in (None, ''):
                wrapper.border = border.all(1, unit_color_dark)
                wrapper.border_radius = 5
                wrapper.update()
        
        options = [dropdown.Option(text = i['label'], key = str(i['value'])) for i in from_list_name]
        options_list = Dropdown(
            options = options,
            value = None,
            dense = True,
            expand = True,
            text_style = TextStyle(size = helper_txt_size, color = input_hint_color),
            hint_style = TextStyle(size = helper_txt_size, color = input_hint_color),
        )
        container_dd = Container(
            expand = True,
            height = txf_height,
            clip_behavior = ClipBehavior.HARD_EDGE,
            content = options_list
        )
        options_list.on_change = lambda e:_on_dd_change(e, options_list, container_dd)

        return Row(alignment = MainAxisAlignment.START, 
            controls = [
                Text(name_info, size = general_txt_size, weight = FontWeight),
                container_dd
            ]
        ), options_list, container_dd

    def _show_chart_reactions(self, risks: list):
        total = sum(int(i.get("count", 0)) for i in risks)
        if not risks or total == 0:
            return
        
        sections = []
        legend_rows = []
        colors = ['#ABCDEF', "#66B0B6", "#EDC58C", "#F0DC8B", "#CAAAE8", "#EBAAB9"]
        radius = 55

        for idx, i in enumerate(risks):
            term = (i.get('term') or '(unknown)').upper()
            count = int(i.get('count', 0))
            pct = round(100 * count / total, 1)
            sections.append(
                PieChartSection(
                    value = count,
                    title = f'{pct}%',
                    color = colors[idx % len(colors)],
                    radius = radius,
                    title_style = TextStyle(size = helper_txt_size, weight = 'bold'),
                    title_position = 0.6
                )
            )
            legend_rows.append(
                Row(
                    spacing = 6,
                    controls = [
                        Container(width = 12, height = 12, bgcolor = colors[idx % len(colors)], border_radius = 2),
                        Text(term, size = helper_txt_size, no_wrap = False, expand = True),
                        Text(str(count), size = helper_txt_size),
                    ],
                )
            )

        legend = Column(controls = legend_rows, spacing = 4)
        chart = Container(
            width = radius * 2 + 20, 
            height = radius * 2 + 50,
            margin = padding.only(left = 5, right = 5, top = 10),
            alignment = alignment.center,
            content = PieChart(
                sections = sections,
                sections_space = 2, 
                center_space_radius = int(radius * 0.4)
            )
        )
        
        self.results_chart_holder.content = Column(
            controls = [chart, legend],
            spacing = 10,
            alignment = MainAxisAlignment.START,
            horizontal_alignment = CrossAxisAlignment.CENTER,
        )

    # Function for generating a query to the API database by pressing a 'Search for risks' button
    def search_risks(self):
        is_valid = True

        if not self.validator.drug_name_correctness(self.user_drug.value):
            self.user_drug.border_color = self.error_border
            self.user_drug.update()
            is_valid = False
        if not self.validator.age_weight_height_correctness(self.user_age.value):
            self.user_age.border_color = self.error_border
            self.user_age.update()
            is_valid = False
        if not self.validator.validate_dropdown(self.user_sex):
            self.container_user_sex.border = border.all(1, self.error_border)
            self.container_user_sex.border_radius = 5
            self.container_user_sex.update()
            is_valid = False
        if not self.validator.validate_dropdown(self.user_country):
            self.container_user_country.border = border.all(1, self.error_border)
            self.container_user_country.border_radius = 5
            self.container_user_country.update()
            is_valid = False

        if not is_valid:
            return    
        else:
            self.btn_search_risks.disabled = True
            self.btn_search_risks.update()

            divider_between_sections = Divider(thickness = 2, color = unit_color_dark)
            result_title = Row(alignment = MainAxisAlignment.CENTER, controls = [Text('Results', weight = FontWeight.BOLD, size = title_txt_size)])
            
            try:
                filters = PatientFilters(
                    gender = int(self.user_sex.value),
                    age = float(self.user_age.value),
                    country = self.user_country.value or None,
                    age_window = 2.0, # +- 2 years
                )
                found_risks = fetch_risks(drug_query = self.user_drug.value, filters = filters)

                if isinstance(found_risks, dict) and found_risks.get('error'):
                    self.results_section.controls.clear()
                    self.results_section.controls.extend([
                        divider_between_sections,
                        result_title,
                        Text(found_risks['error'], size = general_txt_size, text_align = TextAlign.JUSTIFY),
                    ])
                    self.page.update()
                    # try to scroll automatically
                    try:
                        self.check_content.scroll_to(key = 'results_anchor', duration = 400)
                        self.page.update()
                    except Exception as ex:
                        # print(f'Scroll error: {ex}')
                        pass
                    return

                self.results_section.controls.clear()
                self.results_section.controls.extend([
                    divider_between_sections,
                    result_title,
                    Text('The results are based on reports from the last 5 years, filtered according to the information you provided', size = helper_txt_size, text_align = TextAlign.JUSTIFY),
                ])

                results = found_risks.get('results', []) or []
                self._show_chart_reactions(results)
                self.results_section.controls.extend([self.results_chart_holder])
                
                self.check_content.update()
                self.page.update()
                
                # try to scroll automatically
                try:
                    self.check_content.scroll_to(key = 'results_anchor', duration = 400)
                    self.page.update()
                except Exception as ex:
                    # print(f'Scroll error: {ex}')
                    pass


            except Exception as ex:
                # print(f'Error: {ex}')
                self.results_section.controls.clear()
                self.results_section.controls.extend([
                    divider_between_sections,
                    result_title,
                    Text('Error: something went wrong. Please, try later', italic = True),
                ])
                
                try:
                    self.check_content.scroll_to(key='results_anchor', duration=400)
                    self.page.update()
                except Exception as scroll_ex:
                    # print(f'Scroll error: {scroll_ex}')
                    pass

                self.update()

            finally:
                self.btn_search_risks.disabled = False
                self.btn_search_risks.update()

    # Automatically cleaning the result section when go to other page
    def will_unmount(self):
        self.results_section.controls.clear()