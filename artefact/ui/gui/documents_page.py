from flet import *
from artefact.utils.traits import *
from artefact.ui.gui.components.navigation import NavigationBar
from artefact.ui.gui.components.page_header import PageHeader
from artefact.service.notifications import NotificationService
from artefact.service.authentication import auth
from artefact.service import documents_page_service

class DocumentsPage(UserControl):
    
    def __init__(self):
        super().__init__()
        self.expand = True
        self.offset = transform.Offset(0,0,)

        self.token = ''
        self.user_uid = ''
 
        self.no_docs_text = Text('No documents uploaded yet', size = general_txt_size, italic = True, color = Colors.GREY, visible = False)

        # Area for uploaded documents
        self.doc_grid = GridView(
            expand = True,
            max_extent = base_width / 2 - 20,
            spacing = 10,
            run_spacing = 10,
            child_aspect_ratio = 0.9
        )
        self.file_picker_download = FilePicker(on_result = self.download_picked_file)

        # Button to upload new file
        self.file_picker_upload = FilePicker(on_result = self.on_file_picked)
        self.btn_add_file = ElevatedButton(
            content = Text('Add new file', size = general_txt_size, color = Colors.WHITE),
            height = txf_height,
            width = btn_width,
            bgcolor = Dark_bgcolor,
            style = ButtonStyle(shape = RoundedRectangleBorder(radius = 10)),
            on_click = lambda _: self.file_picker_upload.pick_files(
                allow_multiple = False,
                allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
            )
        )


    def build(self):
        self.page.overlay.append(self.file_picker_upload)
        self.page.overlay.append(self.file_picker_download)

        page_header = PageHeader(current_page = None)
        
        self.token = self.page.session.get('token')
        self.user_uid = self.page.session.get('uid')

        # Check the timer to start notification service only once
        if self.token and not self.page.session.get('reminders_started'):
            notif_service = NotificationService(self.page, self.token, page_header = page_header)
            self.page.overlay.append(notif_service)
        

        document_content = Container(
            content = Column(
                spacing = 4,
                controls = [
                    page_header,
                    Row(alignment = MainAxisAlignment.CENTER,
                        controls = [Text('Documents', weight = FontWeight.BOLD, size = 16)]
                    ),
                    self.no_docs_text,
                    Container(
                        expand = True,
                        padding = padding.only(top = 10, bottom = 20),
                        content = self.doc_grid
                    ),
                    Container(
                        margin = padding.only(bottom = 15, top = 10),
                        content = self.btn_add_file
                    )
                ]
            )
        )

        # Properties of Documents page: basic and animation
        self.documents = Row(
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
                content = document_content
            )]
        )

        page_header.current_page = self.documents
        navigation = NavigationBar(current_page = self.documents)

        # Combine Navigation + Documents page
        self.content = Container(
            width = base_width, 
            height = base_height, 
            bgcolor = Light_bgcolor,
            border_radius = b_radius,
            expand = True,
            content = Stack(
                controls = [navigation, self.documents]
            )
        )

        
        return self.content

    def did_mount(self):
        self.load_documents()

    # Open navigation moving the documents page to the right
    def shrink(self, e):
        self.documents.controls[0].width = 70
        self.documents.controls[0].scale = transform.Scale(1, alignment=alignment.center_right)
        self.documents.controls[0].border_radius = border_radius.only(top_left=35, top_right=0, bottom_left=35, bottom_right=0)
        self.documents.update()


    # Logic action of file picker clicking the 'Add new file' button
    def on_file_picked(self, e: FilePickerResultEvent):
        # print("File picker result:", e.files)
        if e.files:
            file_path = e.files[0].path
            documents_page_service.upload_user_document(self.user_uid, self.token, file_path)
            self.load_documents()


    # Function to show uploaded files on the page
    def load_documents(self):
        self.doc_grid.controls.clear()
        try:
            documents = documents_page_service.load_user_documents(self.user_uid, self.token)

            if documents:
                self.no_docs_text.visible = False
                for doc_id, doc in documents.items():
                    self.doc_grid.controls.append(
                        self._build_doc_card(doc['name'], doc['url'], doc['storage_path'], doc_id)
                    )
            else:
                self.no_docs_text.visible = True

        except Exception as e:
            self.no_docs_text.value = f'Failed to load documents: {e}'
            self.no_docs_text.visible = True

        self.update()
        # print('def load_documents finished')

    # Creation of visual of file
    def _build_doc_card(self, name, url, storage_path, doc_id):
        if name.lower().endswith(('.jpg', '.jpeg', '.png')):
            preview = Icon(icons.IMAGE, size = 30)
        else: 
            preview = Icon(icons.PICTURE_AS_PDF, size = 30)

        document_cell = Container(
            # border = border.all(1, unit_color_dark),
            # border_radius = 10,
            # padding = padding.only(bottom = 2, right = 3),
            content = Column(
                spacing = 5,
                tight = True,
                horizontal_alignment = 'center', 
                alignment = 'center',
                controls = [
                    preview,
                    Text(name, size = 10, overflow = TextOverflow.ELLIPSIS, max_lines = 2, text_align = 'center'),
                    Row(
                        alignment = MainAxisAlignment.SPACE_EVENLY,
                        controls = [
                            IconButton(
                                icons.DOWNLOAD,
                                icon_color = unit_color_dark, 
                                icon_size = 20,
                                width = 25,
                                height = 25, 
                                padding = padding.all(0),
                                alignment = alignment.center,
                                on_click = lambda _: self._download_file(name, url)
                            ),
                            IconButton(
                                icons.DELETE,
                                icon_color = unit_color_dark,
                                icon_size = 20, 
                                width = 25,
                                height = 25,
                                padding = padding.all(0),
                                alignment = alignment.center,
                                on_click = lambda _: self._delete_document(doc_id, storage_path)
                            )
                        ]
                    )
                ]
            )
        )

        return document_cell
    
    
    # Functions to download files on the device
    def _download_file(self, name, url):
        self.pending_download = {'name': name, 'url': url, 'token': self.token}
        self.file_picker_download.save_file(file_name = name)

    # File_picker activity
    def download_picked_file(self, e: FilePickerResultEvent):
        if e.path and hasattr(self, 'pending_download'):
            token = self.pending_download['token']
            url = self.pending_download['url']
            documents_page_service.download_file_from_url(url, e.path, token)
            del self.pending_download


    # Function to delete file from the app
    def _delete_document(self, doc_id, storage_path):
        try:
            documents_page_service.delete_user_document(self.user_uid, self.token, doc_id, storage_path)
            self.load_documents()

            self.page.snack_bar = SnackBar(Text('Document successfully deleted'))
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as e:
            # print(f'Failed to delete document: {e}')

            self.page.snack_bar = SnackBar(Text('Failed to delete document'))
            self.page.snack_bar.open = True
            self.page.update()