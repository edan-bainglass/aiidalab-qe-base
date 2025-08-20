import pytest
import traitlets as tl

from aiidalab_qe_base.models.code import PwCodeModel
from aiidalab_qe_base.panels import configuration, panel, resources, results, settings
from aiidalab_qe_base.widgets.widgets import PwCodeResourceSetupWidget


class TestPanel:
    @pytest.fixture(autouse=True)
    def setup(cls):
        cls.model = panel.PanelModel()
        cls.panel = panel.Panel(cls.model)

    def test_model(self):
        assert self.model.title == "Panel"
        assert self.model.identifier == "panel"

    def test_panel(self):
        assert self.panel._model == self.model
        assert self.model.identifier in self.panel.loading_message.message.value
        with pytest.raises(NotImplementedError):
            self.panel.render()


class TestSettingsPanel:
    @pytest.fixture(autouse=True)
    def setup(cls):
        cls.model = settings.SettingsModel()
        cls.panel = settings.SettingsPanel(cls.model)

    def test_model(self):
        assert not self.model.include
        assert not self.model.loaded_from_process

    def test_panel(self):
        assert not self.panel.updated
        assert not self.panel.links


class TestConfigurationSettingsPanel:
    @pytest.fixture(autouse=True)
    def setup(cls):
        cls.model = configuration.ConfigurationSettingsModel()
        cls.panel = configuration.ConfigurationSettingsPanel(cls.model)

    def test_model(self):
        assert not self.model._defaults

    def test_panel(self):
        assert not self.panel.updated
        self.model.add_traits(dummy=tl.Unicode("dummy-trait"))
        self.panel.add_traits(dummy=tl.Unicode())
        link = tl.dlink(
            (self.model, "dummy"),
            (self.panel, "dummy"),
        )
        assert self.panel.dummy == self.model.dummy
        self.panel.links.append(link)
        self.panel.refresh()
        assert not self.panel.links
        assert not self.panel.updated  # model not included - no update triggered
        self.model.include = True
        self.panel.refresh()
        assert self.panel.updated


class TestResourcesPanel:
    @pytest.fixture(autouse=True)
    def setup(cls):
        cls.model = resources.ResourceSettingsModel()
        cls.panel = resources.ResourceSettingsPanel(cls.model)

    def test_model(self, default_user_email, pw_code):
        assert not self.model.global_codes
        assert not self.model.warning_messages
        assert not self.model.default_codes
        assert self.model.DEFAULT_USER_EMAIL == default_user_email

        code_model = PwCodeModel(name="pw")
        self.model.add_model("pw", code_model)
        assert self.model.has_model("pw")
        assert self.model.get_model("pw") is code_model
        assert code_model.selected == pw_code.uuid

        code_model.selected = None
        self.model.refresh_codes()
        assert code_model.selected == pw_code.uuid

        code_model.activate()
        state = self.model.get_model_state()
        assert "pw" in state["codes"]
        assert state["codes"]["pw"] == code_model.get_model_state()

        code_model.selected = None
        self.model.set_model_state({"codes": {"pw": code_model.get_model_state()}})
        assert code_model.selected == pw_code.uuid

    def test_panel(self, default_user_email):
        assert not self.panel.code_widgets
        assert not self.panel.code_widgets_container.children

        array = []
        self.panel._on_code_resource_change = lambda _: array.append("triggered")
        code_model = PwCodeModel(name="pw")
        self.panel.register_code_trait_callbacks(code_model)
        code_model.parallelization_override = True
        assert len(array) == 1
        code_model.num_nodes = 2
        assert len(array) == 2
        code_model.num_cpus = 4
        assert len(array) == 4  # `num_cpus` also updates `ntasks_per_node`

        code_model.activate()
        self.panel.rendered = True
        self.panel._toggle_code(code_model)
        assert "pw" in self.panel.code_widgets
        code_widget = self.panel.code_widgets["pw"]
        assert isinstance(code_widget, PwCodeResourceSetupWidget)
        assert self.panel.code_widgets_container.children[0] == code_widget
        assert code_model.is_rendered
        assert not code_model.options
        code_model.update(default_user_email)
        assert code_model.options
        assert code_widget.code_selection.code_select_dropdown.options
        assert not code_widget.code_selection.code_select_dropdown.disabled
        code_model.options = []
        assert not code_widget.code_selection.code_select_dropdown.options
        assert code_widget.code_selection.code_select_dropdown.disabled


class TestResultsPanel:
    @pytest.fixture(autouse=True)
    def setup(cls):
        cls.model = results.ResultsModel()
        cls.panel = results.ResultsPanel(cls.model)

    # TODO improve mock workchain fixture to include called processes
    # assert self.model.has_results

    def test_model(self, generate_mock_workchain_node):
        process_node = generate_mock_workchain_node()
        self.model.process_uuid = process_node.uuid
        self.model.identifier = "relax"
        assert self.model.include
        self.model.update()
        assert self.model.auto_render == self.model.has_results

    def test_panel(self):
        pass
