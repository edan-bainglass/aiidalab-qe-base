from aiidalab_qe_base.mixins import Confirmable

from ..settings import SettingsModel


class ConfigurationSettingsModel(SettingsModel, Confirmable):
    """Base model for configuration settings models."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._defaults = {}

    def update(self, specific=""):
        """Updates the model.

        Parameters
        ----------
        `specific` : `str`, optional
            If provided, specifies the level of update.
        """
        pass

    def _get_default(self, trait):
        return self._defaults.get(trait, self.traits()[trait].default_value)
