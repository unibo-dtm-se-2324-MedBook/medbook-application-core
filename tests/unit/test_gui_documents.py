import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from artefact.ui.gui.documents_page import DocumentsPage

class SessionMock:
    def __init__(self):
        self._store = {}
    def get(self, key, default=None):
        return self._store.get(key, default)
    def set(self, key, value):
        self._store[key] = value
    def clear(self):
        self._store.clear()

class PageMock:
    def __init__(self):
        self.session = SessionMock()
        self.overlay = []
        self.snack_bar = None
        self.update_calls = 0
    def update(self, *args, **kwargs):
        self.update_calls += 1


@pytest.fixture
def page():
    return PageMock()

@pytest.fixture
def docs_page(page, monkeypatch):
    class DummyNotif:
        def __init__(self, *a, **kw): pass
    monkeypatch.setattr(
        'artefact.ui.gui.documents_page.NotificationService',
        DummyNotif
    )

    page.session.set('token', 'TEST_TOKEN')
    page.session.set('uid', 'TEST_UID')

    dp = DocumentsPage()
    dp.page = page
    dp.build()
    return dp


# TESTS
def test_build_appends_filepickers_and_reads_session(docs_page, page):
    assert docs_page.file_picker_upload in page.overlay
    assert docs_page.file_picker_download in page.overlay
    assert docs_page.token == 'TEST_TOKEN'
    assert docs_page.user_uid == 'TEST_UID'
    assert docs_page.content is not None

def test_build_starts_notification_service_once_when_no_reminders_flag(monkeypatch, page):
    created = {'n': 0}
    class CountNotif:
        def __init__(self, *a, **kw):
            created['n'] += 1
    monkeypatch.setattr('artefact.ui.gui.documents_page.NotificationService', CountNotif)

    page.session.set('token', 'TOK')
    page.session.set('uid', 'UID')
    assert page.session.get('reminders_started') is None

    dp = DocumentsPage()
    dp.page = page
    before_len = len(page.overlay)
    dp.build()

    assert created['n'] == 1
    assert len(page.overlay) == before_len + 3  # upload + download + notification


def test_did_mount_calls_load_documents(docs_page, monkeypatch):
    called = {'n': 0}
    monkeypatch.setattr(docs_page, 'load_documents', lambda: called.__setitem__('n', called['n'] + 1))
    docs_page.did_mount()
    assert called['n'] == 1


def test_shrink_updates_dimensions_and_calls_update(docs_page):
    inner = docs_page.documents.controls[0]
    
    prev_width = getattr(inner, "width", None)
    prev_scale = getattr(inner, "scale", None)
    prev_radius = getattr(inner, "border_radius", None)

    original_update = docs_page.documents.update
    docs_page.documents.update = lambda: None
    try:
        docs_page.shrink(e=None)
    finally:
        docs_page.documents.update = original_update

    assert inner.width == 70
    assert hasattr(inner, "scale") and inner.scale is not None
    assert hasattr(inner, "border_radius") and inner.border_radius is not None
    assert (prev_width, prev_scale, prev_radius) != (inner.width, inner.scale, inner.border_radius)

def test_on_file_picked_uploads_and_reload(docs_page, monkeypatch):
    upload_called = {'args': None}
    monkeypatch.setattr(
        'artefact.ui.gui.documents_page.documents_page_service.upload_user_document',
        lambda uid, tok, path: upload_called.__setitem__('args', (uid, tok, path))
    )

    reload_called = {'n': 0}
    monkeypatch.setattr(docs_page, 'load_documents', lambda: reload_called.__setitem__('n', reload_called['n'] + 1))

    e = SimpleNamespace(files=[SimpleNamespace(path='C:/tmp/file1.pdf')])
    docs_page.on_file_picked(e)

    assert upload_called['args'] == ('TEST_UID', 'TEST_TOKEN', 'C:/tmp/file1.pdf')
    assert reload_called['n'] == 1


def test_on_file_picked_ignores_when_no_files(docs_page, monkeypatch):
    upload = MagicMock()
    monkeypatch.setattr(
        'artefact.ui.gui.documents_page.documents_page_service.upload_user_document',
        upload
    )
    reload_called = {'n': 0}
    monkeypatch.setattr(docs_page, 'load_documents', lambda: reload_called.__setitem__('n', reload_called['n'] + 1))

    docs_page.on_file_picked(SimpleNamespace(files=None))
    upload.assert_not_called()
    assert reload_called['n'] == 0


def test_load_documents_with_data(docs_page, monkeypatch):
    sample_docs = {
        'id1': {'name': 'scan1.jpg', 'url': 'http://u/1', 'storage_path': 'p/1'},
        'id2': {'name': 'report.pdf', 'url': 'http://u/2', 'storage_path': 'p/2'},
    }
    monkeypatch.setattr(
        'artefact.ui.gui.documents_page.documents_page_service.load_user_documents',
        lambda uid, tok: sample_docs
    )

    docs_page.page.update_calls = 0
    docs_page.load_documents()

    assert docs_page.no_docs_text.visible is False
    assert len(docs_page.doc_grid.controls) == len(sample_docs)
    assert docs_page.page.update_calls >= 1


def test_load_documents_empty(docs_page, monkeypatch):
    monkeypatch.setattr(
        'artefact.ui.gui.documents_page.documents_page_service.load_user_documents',
        lambda uid, tok: {}
    )
    docs_page.page.update_calls = 0
    docs_page.load_documents()
    assert docs_page.no_docs_text.visible is True
    assert docs_page.page.update_calls >= 1


def test_load_documents_exception_sets_error_text(docs_page, monkeypatch):
    def raise_err(uid, tok):
        raise RuntimeError('boom')
    monkeypatch.setattr(
        'artefact.ui.gui.documents_page.documents_page_service.load_user_documents',
        raise_err
    )
    docs_page.load_documents()
    assert docs_page.no_docs_text.visible is True
    assert 'Failed to load documents' in docs_page.no_docs_text.value


def test_build_doc_card_preview_and_clicks(docs_page, monkeypatch):
    card_img = docs_page._build_doc_card('photo.JPG', 'http://url-img', 'sp/img', 'doc_img')
    card_pdf = docs_page._build_doc_card('file.pdf', 'http://url-pdf', 'sp/pdf', 'doc_pdf')

    def find_buttons(card):
        col = getattr(card, 'content', None)
        assert col and hasattr(col, 'controls')
        last_row = col.controls[-1]
        assert hasattr(last_row, 'controls') and len(last_row.controls) == 2
        return last_row.controls[0], last_row.controls[1]  # download_btn, delete_btn

    dl_btn, del_btn = find_buttons(card_img)

    called = {'download': None, 'delete': None}
    docs_page._download_file = lambda name, url: called.__setitem__('download', (name, url))
    docs_page._delete_document = lambda doc_id, sp: called.__setitem__('delete', (doc_id, sp))

    dl_btn.on_click(SimpleNamespace())
    del_btn.on_click(SimpleNamespace())

    assert called['download'] == ('photo.JPG', 'http://url-img')
    assert called['delete'] == ('doc_img', 'sp/img')


def test_download_file_sets_pending_and_invokes_filepicker(docs_page, monkeypatch):
    saved = {'name': None}
    docs_page.file_picker_download.save_file = lambda file_name: saved.__setitem__('name', file_name)

    docs_page._download_file('report.pdf', 'http://url')
    assert docs_page.pending_download == {'name': 'report.pdf', 'url': 'http://url', 'token': 'TEST_TOKEN'}
    assert saved['name'] == 'report.pdf'


def test_download_picked_file_uses_service_and_clears_pending(docs_page, monkeypatch):
    docs_page.pending_download = {'name': 'a.pdf', 'url': 'http://u', 'token': 'TEST_TOKEN'}

    called = {'args': None}
    monkeypatch.setattr(
        'artefact.ui.gui.documents_page.documents_page_service.download_file_from_url',
        lambda url, path, token: called.__setitem__('args', (url, path, token))
    )
    e = SimpleNamespace(path='C:/target/a.pdf')
    docs_page.download_picked_file(e)

    assert called['args'] == ('http://u', 'C:/target/a.pdf', 'TEST_TOKEN')
    assert not hasattr(docs_page, 'pending_download')


def test_delete_document_success_shows_snackbar_and_reload(docs_page, monkeypatch):
    del_mock = MagicMock()
    monkeypatch.setattr(
        'artefact.ui.gui.documents_page.documents_page_service.delete_user_document',
        del_mock
    )
    
    # Assume that load_documents was called
    reload_calls = {'n': 0}
    monkeypatch.setattr(docs_page, 'load_documents', lambda: reload_calls.__setitem__('n', reload_calls['n'] + 1))

    docs_page.page.update_calls = 0
    docs_page._delete_document('DOC1', 'sp/1')

    del_mock.assert_called_once_with('TEST_UID', 'TEST_TOKEN', 'DOC1', 'sp/1')
    assert reload_calls['n'] == 1
    assert docs_page.page.snack_bar is not None
    assert getattr(docs_page.page.snack_bar, 'open', False) is True
    assert docs_page.page.update_calls >= 1


def test_delete_document_exception_shows_error_snackbar(docs_page, monkeypatch):
    def raise_delete(uid, tok, doc_id, sp):
        raise RuntimeError('delete failed')
    monkeypatch.setattr(
        'artefact.ui.gui.documents_page.documents_page_service.delete_user_document',
        raise_delete
    )
    docs_page.page.update_calls = 0
    docs_page._delete_document('DOC2', 'sp/2')

    assert docs_page.page.snack_bar is not None
    assert getattr(docs_page.page.snack_bar, 'open', False) is True
    assert 'Failed to delete' in getattr(docs_page.page.snack_bar.content, 'value', '')
    assert docs_page.page.update_calls >= 1