import unittest 
from types import SimpleNamespace  # Creates an object with attributes like a regular class, but from the passed arguments
from unittest.mock import patch
from artefact.ui.gui.first_page import FirstPage

# Stubs / mocks to avoid raising the real Flet Page
class SessionMock: # Placeholder for page.session
    def __init__(self):
        self._store = {}

    def set(self, key, value): # page.session.set
        self._store[key] = value

class PageMock:
    def __init__(self):
        self.session = SessionMock()
        self.last_route = None

    def go(self, route: str):
        self.last_route = route

class EmailStub: # instead TextField
    def __init__(self, value: str = ''):
        self.value = value
        self.border_color = None
        self.updated = False

    def update(self):
        self.updated = True


class Test_GUI_FirstPage(unittest.TestCase):
    def setUp(self):
        self.fp = FirstPage()
        self.fp.page = PageMock()
        self.fp.build()

    def test_build_creates_content(self):
        self.assertIsNotNone(self.fp.content)
        self.assertIsNotNone(self.fp.email)

    def test_invalid_email_highlights_and_updates(self):
        self.fp.validator = SimpleNamespace(email_correctness = lambda _: False)
        self.fp.email = EmailStub(value = 'not_an_email')

        self.fp.check_email(e = None) # as if we clicked 'Continue'
        self.assertEqual(self.fp.email.border_color, self.fp.error_border)

        self.assertTrue(self.fp.email.updated)
        self.assertIsNone(self.fp.page.last_route)


class Test_Routing(unittest.TestCase):
    def setUp(self):
        self.fp = FirstPage()
        self.fp.page = PageMock()
        self.fp.build()

    def test_existing_user_goes_login(self):
        self.fp.validator = SimpleNamespace(email_correctness = lambda _: True)
        self.fp.email = EmailStub(value = 'user@example.com') # valid email

        with patch("artefact.ui.gui.first_page.check_email", return_value=True):
            self.fp.check_email(e=None)

        self.assertEqual(self.fp.page.session._store.get("email"), "user@example.com")
        self.assertEqual(self.fp.page.last_route, "/login_page")

    def test_new_user_goes_signup(self):
        self.fp.validator = SimpleNamespace(email_correctness = lambda _: True)
        self.fp.email = EmailStub(value = 'newuser@example.com')

        with patch('artefact.ui.gui.first_page.check_email', return_value = False): # user exists? -> no
            self.fp.check_email(e = None)

        self.assertEqual(self.fp.page.session._store.get('email'), 'newuser@example.com')
        self.assertEqual(self.fp.page.last_route, '/signup_page')