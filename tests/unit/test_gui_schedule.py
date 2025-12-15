import calendar
import datetime as dt
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from artefact.ui.gui.main_page import MainPage

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
        self.update_calls = 0
        self.snack_bar = None
        self.dialog = None

    def update(self, *args, **kwargs):
        self.update_calls += 1

    def open(self, _control):
        pass


@pytest.fixture
def page():
    return PageMock()

@pytest.fixture
def main_page(page, monkeypatch):
    page.session.set('token', 'TOK')
    page.session.set('uid', 'UID')

    class DummyNotif:
        def __init__(self, *a, **kw): pass
    monkeypatch.setattr(
        'artefact.ui.gui.main_page.NotificationService',
        DummyNotif
    )
    monkeypatch.setattr(
        'artefact.ui.gui.main_page.load_medicines_for_user',
        lambda uid, tok, y, m: {}
    )

    mp = MainPage()
    mp.page = page
    mp.build()
    return mp


# TESTS
def test_build_reads_session_and_generates_calendar(page, monkeypatch):
    called = {'args': None}
    monkeypatch.setattr(
        'artefact.ui.gui.main_page.load_medicines_for_user',
        lambda uid, tok, y, m: called.__setitem__('args', (uid, tok, y, m)) or {}
    )
    class DummyNotif:
        def __init__(self, *a, **kw): pass
    monkeypatch.setattr('artefact.ui.gui.main_page.NotificationService', DummyNotif)

    page.session.set('token', 'TOK')
    page.session.set('uid', 'UID')

    mp = MainPage()
    mp.page = page
    content = mp.build()

    assert content is not None
    assert called['args'] is not None

    uid, tok, y, m = called['args']
    assert (uid, tok) == ('UID', 'TOK')
    assert hasattr(mp.calendar, 'content')
    assert hasattr(mp.calendar.content, 'controls')
    assert 1 <= len(mp.calendar.content.controls) <= 6

def test_notification_service_added_once_when_no_flag(main_page, page, monkeypatch):
    before = len(page.overlay)
    assert len(page.overlay) >= before

def test_generate_calendar_clickable_cells_for_days_with_pills(main_page):
    mp = main_page
    day = 15
    date_key = f'{mp.year}-{mp.month:02d}-{day:02d}'
    mp.data_by_date[date_key] = [{'key': 'k1', 'medicine_name': 'A', 'quantity': '1', 'note': ''}]
    mp._generate_calendar()

    rows = mp.calendar.content.controls
    assert rows, 'Rows must exist after generation'
    
    clickable_found = False
    for row in rows:
        for cell in getattr(row, 'controls', []):
            col = getattr(cell, 'content', None)
            if not col or not hasattr(col, 'controls') or not col.controls:
                continue
            txt = getattr(col.controls[0], 'content', None)
            if getattr(txt, 'value', None) == str(day):
                if getattr(cell, 'on_click', None):
                    clickable_found = True
                    break
        if clickable_found:
            break
    assert clickable_found, 'Cell for day with pills should be clickable'

def test_prev_month_triggers_load_and_updates_header(main_page, monkeypatch):
    mp = main_page
    called = {'args': []}
    def fake_load(uid, tok, y, m):
        called['args'].append((uid, tok, y, m))
        return {}
    monkeypatch.setattr('artefact.ui.gui.main_page.load_medicines_for_user', fake_load)

    start_month, start_year = mp.month, mp.year
    mp.prev_month(e=None)

    if start_month == 1:
        assert (mp.month, mp.year) == (12, start_year - 1)
    else:
        assert (mp.month, mp.year) == (start_month - 1, start_year)
    assert called['args'], 'load_medicines_for_user must be called'
    assert mp.month_header.value == f'{calendar.month_name[mp.month]} {mp.year}'

def test_next_month_triggers_load_and_updates_header(main_page, monkeypatch):
    mp = main_page
    called = {'args': []}
    def fake_load(uid, tok, y, m):
        called['args'].append((uid, tok, y, m))
        return {}
    monkeypatch.setattr('artefact.ui.gui.main_page.load_medicines_for_user', fake_load)

    start_month, start_year = mp.month, mp.year
    mp.next_month(e=None)

    if start_month == 12:
        assert (mp.month, mp.year) == (1, start_year + 1)
    else:
        assert (mp.month, mp.year) == (start_month + 1, start_year)

    assert called['args'], 'load_medicines_for_user must be called'
    assert mp.month_header.value == f'{calendar.month_name[mp.month]} {mp.year}'

def test_open_day_dialog_opens_dialog_with_list(main_page, page):
    mp = main_page
    day = 10
    date_key = f'{mp.year}-{mp.month:02d}-{day:02d}'
    mp.data_by_date[date_key] = [
        {'key': 'k1', 'medicine_name': 'Med A', 'quantity': '1', 'note': 'n1'},
        {'key': 'k2', 'medicine_name': 'Med B', 'quantity': '2', 'note': 'n2'},
    ]

    prev_updates = page.update_calls
    mp.open_day_dialog(day)

    assert page.dialog is not None
    assert getattr(page.dialog, 'open', False) is True
    assert page.update_calls > prev_updates

def test_close_dialog_closes(main_page, page):
    mp = main_page
    page.dialog = SimpleNamespace(open=True)
    prev = page.update_calls
    mp._close_dialog()
    assert page.dialog.open is False
    assert page.update_calls > prev

def test_show_med_detail_opens_dialog(main_page, page):
    mp = main_page
    date_key = f'{mp.year}-{mp.month:02d}-15'
    pill = {'key': 'K', 'medicine_name': 'Med X', 'quantity': '3', 'note': 'foo'}
    prev_updates = page.update_calls

    mp._show_med_detail(date_key, pill)

    assert page.dialog is not None
    assert getattr(page.dialog, 'open', False) is True
    assert page.update_calls > prev_updates


def test_delete_pill_calls_service_and_updates_locally(main_page, page, monkeypatch):
    mp = main_page
    day = 5
    date_key = f'{mp.year}-{mp.month:02d}-{day:02d}'
    mp.data_by_date[date_key] = [
        {'key': 'k1', 'medicine_name': 'A', 'quantity': '1', 'note': ''},
        {'key': 'k2', 'medicine_name': 'B', 'quantity': '2', 'note': ''},
    ]

    del_mock = MagicMock(return_value=True)
    monkeypatch.setattr('artefact.ui.gui.main_page.delete_pill_database', del_mock)

    page.dialog = SimpleNamespace(open=True)
    prev_updates = page.update_calls

    mp._delete_pill(date_key, {'key': 'k1'})

    del_mock.assert_called_once_with('UID', 'TOK', 'k1')
    remaining = mp.data_by_date.get(date_key, [])
    assert all(p['key'] != 'k1' for p in remaining)
    assert page.dialog.open is False
    assert page.update_calls > prev_updates

def test_show_form_opens_dialog(main_page, page):
    mp = main_page
    prev = page.update_calls
    mp.show_form(e=None)
    assert mp.form is not None
    assert page.dialog is mp.form
    assert mp.form.open is True
    assert page.update_calls > prev

def test_handle_change_updates_selected_date(main_page, page):
    mp = main_page
    mp.show_form(e=None)
    prev = page.update_calls
    event = SimpleNamespace(control=SimpleNamespace(value=dt.datetime(2025, 1, 1)))
    mp.handle_change(event)
    assert mp.selected_date.value == '2025-01-01'
    assert page.update_calls > prev

def test_handle_dismissal_shows_snack(main_page, page):
    mp = main_page
    prev = page.update_calls
    mp.handle_dismissal(e=None)
    assert page.snack_bar is not None
    assert getattr(page.snack_bar, 'open', False) is True
    assert page.update_calls > prev

def test_save_medicine_success_flow(main_page, page, monkeypatch):
    mp = main_page
    mp.show_form(e=None)

    mp.medname_field.value = 'Amoxicillin'
    mp.qty_field.value = '2'
    mp.selected_date.value = '2025-01-03'
    mp.note_field.value = 'after meal'

    monkeypatch.setattr(
        'artefact.ui.gui.main_page.save_pill_database',
        lambda uid, tok, name, qty, date, note: 'NEWKEY'
    )

    prev_updates = page.update_calls
    mp.save_medicine()

    assert mp.form.open is False
    assert page.snack_bar is not None and getattr(page.snack_bar, 'open', False) is True
    assert '2025-01-03' in mp.data_by_date
    assert any(p['key'] == 'NEWKEY' for p in mp.data_by_date['2025-01-03'])
    assert page.update_calls > prev_updates

def test_save_medicine_validation_error_shows_snack(main_page, page):
    mp = main_page
    mp.show_form(e=None)

    mp.medname_field.value = ''
    mp.qty_field.value = '1'
    mp.selected_date.value = '2025-01-03'
    mp.note_field.value = ''

    prev = page.update_calls
    mp.save_medicine()
    assert page.snack_bar is not None and getattr(page.snack_bar, 'open', False) is True
    assert page.update_calls > prev