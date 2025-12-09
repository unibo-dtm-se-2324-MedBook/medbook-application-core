import pytest                       
from types import SimpleNamespace
from unittest.mock import patch      
from artefact.ui.gui.login_page import LoginPage

# Stubs / mocks to avoid raising the real Flet Page
class SessionMock: # Placeholder for page.session
    def __init__(self):
        self._store = {}  # internal key-value storage

    def get(self, key, default = None): # page.session.get(...)
        return self._store.get(key, default)

    def set(self, key, value):
        self._store[key] = value

class PageMock:
    def __init__(self):
        self.session = SessionMock()
        self.last_route = None
        self.splash = None
        self.snack_bar = None
        self.update_calls = 0 # update() call counter

    def go(self, route: str):
        self.last_route = route

    def update(self):
        self.update_calls += 1 # as a check we assume that there was a call

class PasswordStub: # Placeholder instead of TextField for password
    def __init__(self, value = '', masked = True):
        self.value = value
        self.password = masked # visible / nonvisible
        self.border_color = None
        self.updated = False

    def update(self):
        self.updated = True

class TextStub: # Placeholder instead of Text
    def __init__(self, value = ''):
        self.value = value
        self.updated = False

    def update(self):
        self.updated = True


@pytest.fixture 
def page(): # Return a new mock Page object for each test
    return PageMock()

@pytest.fixture
def login_page(page):
    page.session.set('email', 'user@example.com')
    lp = LoginPage()
    lp.page = page
    lp.build()
    return lp


# Tests
## Check if the basic elements exist
def test_build_reads_email_and_sets_label(login_page):
    lp = login_page
    assert lp.email == 'user@example.com'
    assert lp.text_email.value == 'Email: user@example.com'
    assert lp.password is not None
    assert lp.login_content is not None
    assert lp.content is not None

    # continue_container = None
    # for c in getattr(lp.login_content, 'controls', []):
    #     if hasattr(c, 'on_click') and c.on_click is lp.continuing:
    #         continue_container = c
    #         break
    # assert continue_container is not None


def test_show_hide_password_toggles(login_page):
    lp = login_page
    lp.password = PasswordStub(value = '', masked = True)
    lp.view_passw = TextStub(value = 'View')

    # Open password
    lp.show_hide_passw(e = None)
    assert lp.password.password is False # password is not hidden
    assert lp.view_passw.value == 'Hide'
    assert lp.password.updated is True
    assert lp.view_passw.updated is True

    # Hide password
    lp.password.updated = False
    lp.view_passw.updated = False
    lp.show_hide_passw(e = None)
    assert lp.password.password is True # password is hidden
    assert lp.view_passw.value == "View"
    assert lp.password.updated is True
    assert lp.view_passw.updated is True


def test_continuing_with_invalid_password_shows_error(login_page, page):
    lp = login_page

    lp.validator = SimpleNamespace(password_correctness = lambda _: False)
    lp.password = PasswordStub(value = 'wrong_password', masked = True)
    lp.continuing(e = None)

    assert lp.password.border_color == lp.error_border
    assert lp.password.updated is True
    assert page.last_route is None # stay on this page


def test_continuing_with_valid_password_and_success_token(login_page, page):
    lp = login_page

    lp.validator = SimpleNamespace(password_correctness = lambda _: True)
    lp.password = PasswordStub(value = 'correct_password', masked=True)

    with patch('artefact.ui.gui.login_page.login_user', return_value = 'TOKEN1') as mock_login, \
         patch('artefact.ui.gui.login_page.store_token') as mock_store, \
         patch('artefact.ui.gui.login_page.firebase_auth.verify_id_token',
            return_value={'uid': 'UID1'}) as mock_verify:

        lp.continuing(e = None)

        mock_login.assert_called_once_with(lp.email, 'correct_password')
        mock_store.assert_called_once_with('TOKEN1')
        mock_verify.assert_called_once_with('TOKEN1')

        assert page.session.get('token') == 'TOKEN1'
        assert page.session.get('uid') == 'UID1'
        assert page.last_route == '/main_page' # successful login
        assert page.update_calls >= 2

def test_continuing_with_valid_password_and_failed_login(login_page, page):
    lp = login_page

    lp.validator = SimpleNamespace(password_correctness = lambda _: True)
    lp.password = PasswordStub(value = 'correct_password', masked = True)

    with patch('artefact.ui.gui.login_page.login_user', return_value = None) as mock_login, \
         patch('artefact.ui.gui.login_page.store_token') as mock_store:

        lp.continuing(e = None)
        mock_login.assert_called_once_with(lp.email, 'correct_password')

        mock_store.assert_not_called() # store_token is not be called because no token exists

        assert page.snack_bar is not None # SnackBar
        assert getattr(page.snack_bar, 'open', False) is True

        assert page.last_route is None # unsuccessful login


def test_forgot_password_link_navigates(login_page, page):
    lp = login_page
    forgot_container = None

    for ctrl in getattr(lp.login_content, 'controls', []): # Looking for a container link with the text "Forgot your password"
        if hasattr(ctrl, 'on_click') and ctrl.on_click is not None:
            row = getattr(ctrl, 'content', None)
            if row and hasattr(row, 'controls'):
                has_forgot_text = any(
                    getattr(sub, 'value', '') == 'Forgot your password?'
                    for sub in row.controls
                )
                if has_forgot_text:
                    forgot_container = ctrl
                    break

    assert forgot_container is not None, 'Forgot password link container not found'
    forgot_container.on_click(SimpleNamespace())
    assert page.last_route == '/passw_page'
