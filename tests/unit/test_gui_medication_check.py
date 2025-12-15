import pytest
from flet import transform, Text
#  alignment, border_radius
from types import SimpleNamespace
from artefact.ui.gui.medication_check_page import MedicineCheckPage
from artefact.utils.traits import unit_color_dark

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
        self.dialog = None
        self.snack_bar = None
    def update(self, *args, **kwargs):
        self.update_calls += 1
    def open(self, _control):
        pass


# Replaces .update() with a no-op if the method exists
def _noop_update(obj):
    if hasattr(obj, 'update'):
        obj.update = lambda *a, **k: None


@pytest.fixture
def page():
    return PageMock()

@pytest.fixture
def med_page(page, monkeypatch):
    page.session.set('token', 'TOK')

    class DummyNotif:
        def __init__(self, *a, **kw): pass

    monkeypatch.setattr('artefact.ui.gui.medication_check_page.NotificationService', DummyNotif)

    mp = MedicineCheckPage()
    mp.page = page
    mp.build()
    return mp

@pytest.fixture
def med_page_safe(med_page):
    mp = med_page
    # Text fields
    _noop_update(mp.user_drug)
    _noop_update(mp.user_age)
    # Dropdown containers
    _noop_update(mp.container_user_sex)
    _noop_update(mp.container_user_country)
    # Elements updated in search_risks
    _noop_update(mp.btn_search_risks)
    _noop_update(mp.check_content)
    _noop_update(mp.results_section)
    _noop_update(mp.results_chart_holder)
    return mp

# TESTS
def test_build_reads_token_and_appends_notif_service(page, monkeypatch):
    page.session.set('token', 'TOK')

    added = {'count': 0}
    class DummyNotif:
        def __init__(self, *a, **kw):
            added['count'] += 1

    monkeypatch.setattr('artefact.ui.gui.medication_check_page.NotificationService', DummyNotif)

    mp = MedicineCheckPage()
    mp.page = page
    content = mp.build()

    assert content is not None
    assert added['count'] >= 1

def test_txtfield_on_change_sets_border_and_updates(med_page_safe, page):
    mp = med_page_safe
    tf = mp.user_drug
    tf.value = 'Ibuprofen'

    tf.on_change(SimpleNamespace())  # .update() уже заглушен

    assert getattr(tf, 'border_color', None) == unit_color_dark

def test_dropdown_on_change_sets_border_and_updates(med_page_safe, page):
    mp = med_page_safe
    dd = mp.user_sex
    wrapper = mp.container_user_sex

    dd.value = '1'
    dd.on_change(SimpleNamespace())

    assert getattr(wrapper, 'border', None) is not None
    assert getattr(wrapper, 'border_radius', None) == 5

def test_show_chart_reactions_ignores_empty(med_page):
    mp = med_page

    mp._show_chart_reactions([])
    assert mp.results_chart_holder.content is None

    mp._show_chart_reactions([{'term': 'X', 'count': 0}])
    assert mp.results_chart_holder.content is None


def test_show_chart_reactions_renders_pie_and_legend(med_page):
    mp = med_page
    data = [
        {'term': 'Headache', 'count': 5},
        {'term': 'Nausea', 'count': 3},
    ]
    mp._show_chart_reactions(data)

    col = mp.results_chart_holder.content
    assert col is not None
    assert hasattr(col, 'controls') and len(col.controls) >= 2  # chart + legend

def test_search_risks_validation_errors_early_return(med_page_safe, monkeypatch):
    mp = med_page_safe
    mp.user_drug.value = ''
    mp.user_age.value = ''
    mp.user_sex.value = None
    mp.user_country.value = None

    called = {'fetch': 0}
    monkeypatch.setattr(
        'artefact.ui.gui.medication_check_page.fetch_risks',
        lambda *a, **k: called.__setitem__('fetch', called['fetch'] + 1),
    )
    mp.search_risks()

    assert called['fetch'] == 0
    assert mp.user_drug.border_color == mp.error_border
    assert mp.user_age.border_color == mp.error_border
    assert getattr(mp.container_user_sex, 'border', None) is not None
    assert getattr(mp.container_user_country, 'border', None) is not None
    assert mp.btn_search_risks.disabled in (False, None)

def test_search_risks_success_flow_builds_result_and_chart(med_page_safe, monkeypatch, page):
    mp = med_page_safe
    mp.user_drug.value = 'ibuprofen'
    mp.user_age.value = '26'
    mp.user_sex.value = '1'
    mp.user_country.value = 'IT'

    monkeypatch.setattr(
        'artefact.ui.gui.medication_check_page.PatientFilters',
        lambda **kw: SimpleNamespace(**kw),
    )
    monkeypatch.setattr(
        'artefact.ui.gui.medication_check_page.fetch_risks',
        lambda drug_query, filters: {
            'results': [
                {'term': 'Headache', 'count': 4},
                {'term': 'Nausea', 'count': 2},
            ]
        },
    )

    mp.search_risks()
    assert mp.btn_search_risks.disabled is False
    assert hasattr(mp.results_section, 'controls')
    assert len(mp.results_section.controls) >= 3
    assert mp.results_chart_holder.content is not None


def test_search_risks_api_returns_error_dict(med_page_safe, monkeypatch):
    mp = med_page_safe
    mp.user_drug.value = 'ibuprofen'
    mp.user_age.value = '26'
    mp.user_sex.value = '1'
    mp.user_country.value = 'IT'

    monkeypatch.setattr(
        'artefact.ui.gui.medication_check_page.PatientFilters',
        lambda **kw: SimpleNamespace(**kw),
    )
    monkeypatch.setattr(
        'artefact.ui.gui.medication_check_page.fetch_risks',
        lambda drug_query, filters: {'error': 'Service unavailable'},
    )

    mp.search_risks()
    assert hasattr(mp.results_section, 'controls')
    assert len(mp.results_section.controls) >= 2
    assert mp.btn_search_risks.disabled is False

def test_search_risks_api_returns_error_dict(med_page_safe, monkeypatch):
    mp = med_page_safe
    mp.user_drug.value = 'ibuprofen'
    mp.user_age.value = '26'
    mp.user_sex.value = '1'
    mp.user_country.value = 'IT'

    monkeypatch.setattr(
        'artefact.ui.gui.medication_check_page.PatientFilters',
        lambda **kw: SimpleNamespace(**kw),
    )
    monkeypatch.setattr(
        'artefact.ui.gui.medication_check_page.fetch_risks',
        lambda drug_query, filters: {'error': 'Service unavailable'},
    )

    mp.search_risks()
    assert hasattr(mp.results_section, 'controls')
    assert len(mp.results_section.controls) >= 2  # divider + title + error
    assert mp.btn_search_risks.disabled is False

def test_search_risks_exception_branch_calls_update_and_shows_message(med_page_safe, monkeypatch):
    mp = med_page_safe

    mp.user_drug.value = 'ibuprofen'
    mp.user_age.value = '26'
    mp.user_sex.value = '1'
    mp.user_country.value = 'IT'

    import artefact.ui.gui.medication_check_page as mcp
    monkeypatch.setattr(mcp, 'PatientFilters', lambda **kw: SimpleNamespace(**kw))

    def boom(*a, **k):
        raise RuntimeError('boom')
    monkeypatch.setattr(mcp, 'fetch_risks', boom)

    mp.search_risks()
    texts = [c for c in mp.results_section.controls if isinstance(c, Text)]
    assert any('Error: something went wrong' in getattr(t, 'value', '') for t in texts)
    assert mp.btn_search_risks.disabled is False

def test_will_unmount_clears_results(med_page):
    mp = med_page
    mp.results_section.controls.extend([SimpleNamespace(), SimpleNamespace()])
    assert len(mp.results_section.controls) >= 2
    mp.will_unmount()
    assert mp.results_section.controls == []

def test_shrink_uses_settings_and_updates(med_page_safe):
    mp = med_page_safe

    class DummyBox:
        def __init__(self):
            self.width = None
            self.scale = None
            self.border_radius = None

    class DummySettings:
        def __init__(self):
            self.controls = [DummyBox()]
            self.updated = False
        def update(self):
            self.updated = True

    mp.settings = DummySettings()
    mp.shrink(e=None)

    inner = mp.settings.controls[0]
    assert inner.width == 70
    assert isinstance(inner.scale, transform.Scale)
    assert inner.border_radius is not None
    assert mp.settings.updated is True