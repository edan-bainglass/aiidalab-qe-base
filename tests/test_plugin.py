import pytest

from aiidalab_qe_base.models.code import PwCodeModel
from aiidalab_qe_base.plugin.outline import PluginOutline
from aiidalab_qe_base.plugin.panels.resources import (
    PluginResourceSettingsModel,
    PluginResourceSettingsPanel,
)


def test_panel_outline():
    outline: PluginOutline = PluginOutline()
    assert not outline.include.value
    outline.include.value = True
    assert outline.include.value


class TestPluginResourcePanel:
    @pytest.fixture(autouse=True)
    def setup(cls, pw_code):
        cls.pw_code = pw_code
        cls.model = PluginResourceSettingsModel()
        cls.panel = PluginResourceSettingsPanel(cls.model)
        cls.code_model = PwCodeModel(name="pw")
        cls.model.add_model("pw", cls.code_model)

        code_uuid = pw_code.uuid if pw_code else "dummy-uuid"
        cls.model.global_codes = {
            "quantumespresso__pw": {
                "code": code_uuid,
                "nodes": 2,
                "cpus": 4,
                "ntasks_per_node": 4,
                "cpus_per_task": 1,
                "max_wallclock_seconds": 600,
            }
        }

    def test_model(self):
        assert self.code_model.selected == self.pw_code.uuid
        assert self.code_model.num_nodes == 2
        assert self.code_model.num_cpus == 4

        self.code_model.num_nodes = 1
        self.model.override = True
        assert self.code_model.num_nodes == 1

        state = self.model.get_model_state()
        assert state["override"]

        self.model.override = False
        self.model.set_model_state({"override": True})
        assert self.model.override

    def test_panel(self):
        self.panel.render()

        code_widget = self.panel.code_widgets["pw"]
        assert code_widget.num_cpus.disabled
        assert code_widget.num_nodes.disabled

        self.model.override = True
        self.code_model.selected = None
        assert code_widget.code_selection.code_select_dropdown.value is None

        self.model.override = False
        selected = self.code_model.selected
        assert code_widget.code_selection.code_select_dropdown.value == selected
