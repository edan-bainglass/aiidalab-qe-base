import ipywidgets as ipw
import pytest
import traitlets as tl

from aiidalab_qe_base.widgets import (
    HBoxWithUnits,
    InfoBox,
    LazyLoader,
    LinkButton,
    ParallelizationSettings,
    ProgressBar,
    PwCodeResourceSetupWidget,
    QEAppComputationalResourcesWidget,
    ResourceDetailSettings,
    TableWidget,
)


def test_infobox():
    """Test `InfoBox` classes."""

    custom_classes = ["custom-1", "custom-2 custom-3"]
    infobox: InfoBox = InfoBox(classes=custom_classes)
    assert all(
        css_class in infobox._dom_classes
        for css_class in (
            "info-box",
            "custom-1",
            "custom-2",
            "custom-3",
        )
    )


def test_link_button():
    btn: LinkButton = LinkButton(description="Open", link="#", disabled=False)
    assert "disabled" not in btn._dom_classes
    btn.disabled = True
    assert "disabled" in btn._dom_classes


def test_table_widget():
    table: TableWidget = TableWidget()
    data = [["h1", "h2"], [1, 2], [3, 4]]
    table.data = data
    assert table.data == data
    table.selected_rows = [1]
    assert table.selected_rows == [1]


def test_hbox_with_units():
    widget: ipw.IntText = ipw.IntText(value=5)
    box: HBoxWithUnits = HBoxWithUnits(widget, "eV")
    assert widget in box.children
    assert "hbox-with-units" in box._dom_classes


def test_lazy_loader():
    created = {}

    class Dummy(ipw.HTML):
        def __init__(self, **kwargs):
            created["ok"] = True
            super().__init__(value="x", **kwargs)

    loader: LazyLoader = LazyLoader(Dummy, {})
    assert not loader.rendered
    loader.render()
    assert loader.rendered
    assert created["ok"]
    assert isinstance(loader.children[0], Dummy)


def test_progress_bar():
    pb: ProgressBar = ProgressBar()

    with pytest.raises(tl.TraitError):
        pb.value = 1.2

    with pytest.raises(tl.TraitError):
        pb.value = ProgressBar.AnimationRate(-0.1)

    pb.value = ProgressBar.AnimationRate(0.0)
    pb.value = 0.5


def test_resource_detail_settings():
    widget: ResourceDetailSettings = ResourceDetailSettings()
    params = {
        "ntasks_per_node": 2,
        "cpus_per_task": 3,
        "max_wallclock_seconds": 3600,
    }
    widget.parameters = params
    assert widget.parameters == params
    widget.reset()
    assert widget.parameters == {
        "ntasks_per_node": 1,
        "cpus_per_task": 1,
        "max_wallclock_seconds": 43200,
    }


def test_qe_resources_widget(monkeypatch):
    widget: QEAppComputationalResourcesWidget = QEAppComputationalResourcesWidget(
        description="dos",
        default_calc_job_plugin="quantumespresso.dos",
    )
    params = {
        "code": None,
        "nodes": 2,
        "cpus": 4,
        "ntasks_per_node": 4,
        "cpus_per_task": 1,
        "max_wallclock_seconds": 600,
    }
    widget.parameters = params
    assert widget.get_parameters() == params


def test_parallelization_settings():
    widget: ParallelizationSettings = ParallelizationSettings()
    assert widget.npool.layout.display == "none"
    widget.override.value = True
    assert widget.npool.layout.display == "block"
    widget.npool.value = 2
    widget.reset()
    assert widget.npool.value == 1


def test_pw_code_resource_widget():
    widget: PwCodeResourceSetupWidget = PwCodeResourceSetupWidget(
        description="pw",
        default_calc_job_plugin="quantumespresso.pw",
    )
    params = {
        "code": None,
        "nodes": 1,
        "cpus": 1,
        "ntasks_per_node": 1,
        "cpus_per_task": 1,
        "max_wallclock_seconds": 600,
        "parallelization": {"npool": 3},
    }
    widget.set_parameters(params)
    got = widget.get_parameters()
    assert got["parallelization"] == {"npool": 3}
