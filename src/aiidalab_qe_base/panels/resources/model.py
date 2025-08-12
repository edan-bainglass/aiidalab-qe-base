import traitlets as tl
from aiida import orm

from aiidalab_qe_base.mixins import HasModels
from aiidalab_qe_base.models import CodeModel

from ..settings import SettingsModel


class ResourceSettingsModel(SettingsModel, HasModels[CodeModel]):
    """Base model for resource setting models."""

    global_codes = tl.Dict(
        key_trait=tl.Unicode(),
        value_trait=tl.Dict(),
    )

    warning_messages = tl.Unicode("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Used by the code-setup thread to fetch code options
        self.DEFAULT_USER_EMAIL = orm.User.collection.get_default().email

    def add_model(self, identifier, model):
        super().add_model(identifier, model)
        model.update(self.DEFAULT_USER_EMAIL)

    def refresh_codes(self):
        for _, code_model in self.get_models():
            code_model.update(self.DEFAULT_USER_EMAIL, refresh=True)

    def get_model_state(self):
        return {
            "codes": {
                identifier: code_model.get_model_state()
                for identifier, code_model in self.get_models()
                if code_model.is_ready
            },
        }

    def set_model_state(self, parameters: dict):
        self.set_selected_codes(parameters.get("codes", {}))

    def get_selected_codes(self) -> dict[str, dict]:
        return {
            identifier: code_model.get_model_state()
            for identifier, code_model in self.get_models()
            if code_model.is_ready
        }

    def set_selected_codes(self, code_data):  # TODO =DEFAULT["codes"]
        for identifier, code_model in self.get_models():
            if identifier in code_data:
                code_model.set_model_state(code_data[identifier])

    def _check_blockers(self):
        return []
