from aiidalab_qe_base.plugin.outline import PluginOutline


def test_panel_outline():
    """Test PanelOutline class."""

    outline = PluginOutline()
    assert not outline.include.value
    outline.include.value = True
    assert outline.include.value
