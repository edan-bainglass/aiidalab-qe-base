from aiidalab_qe_base.mixins import Confirmable

from ..settings import SettingsModel


class ConfigurationSettingsModel(SettingsModel, Confirmable):
    """Base model for configuration settings models."""

    def update(self, specific=""):
        """Updates the model.

        Parameters
        ----------
        `specific` : `str`, optional
            If provided, specifies the level of update.
        """
        pass
