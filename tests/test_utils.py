from datetime import datetime, timedelta, timezone

import pytest

from aiidalab_qe_base import utils


class DummyOptions(dict):
    def __init__(self):
        self.resources = {}

    def __setitem__(self, key, value):
        super().__setitem__(key, value)


class DummyMetadata:
    def __init__(self):
        self.options = DummyOptions()


class DummyComponent:
    def __init__(self):
        self.metadata = DummyMetadata()
        self.parallelization = None
        self.settings = None


class DummyComputer:
    def __init__(self, scheduler_type: str):
        self.scheduler_type = scheduler_type


class DummyCode:
    def __init__(self, scheduler_type: str):
        self.computer = DummyComputer(scheduler_type)


def test_set_component_resources_direct():
    component = DummyComponent()
    code_info = {
        "code": DummyCode("core.direct"),
        "nodes": 2,
        "ntasks_per_node": 4,
        "cpus_per_task": 1,
        "max_wallclock_seconds": 600,
    }
    utils.set_component_resources(component, code_info)

    assert component.metadata.options.resources["num_machines"] == 2
    assert component.metadata.options.resources["num_mpiprocs_per_machine"] == 4
    assert component.metadata.options.resources["num_cores_per_mpiproc"] == 1

    assert component.metadata.options["max_wallclock_seconds"] == 600


def test_set_component_resources_hyperqueue():
    component = DummyComponent()
    code_info = {
        "code": DummyCode("hyperqueue"),
        "nodes": 2,
        "ntasks_per_node": 3,
        "cpus_per_task": 4,
        "max_wallclock_seconds": 600,
    }
    utils.set_component_resources(component, code_info)
    assert component.metadata.options.resources["num_cpus"] == 2 * 3 * 4


def test_enable_pencil_decomposition():
    component = DummyComponent()
    utils.enable_pencil_decomposition(component)
    assert component.settings is not None
    assert component.settings.get_dict()["CMDLINE"] == ["-pd", ".true."]


def test_shallow_copy_nested_dict():
    shared = [1, 2]
    original = {"a": {"b": shared}}
    copied = utils.shallow_copy_nested_dict(original)

    assert original is not copied
    assert original["a"] is not copied["a"]
    assert copied["a"]["b"] is shared


def test_format_time():
    t = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert utils.format_time(t) == "2024-01-01 12:00:00"


@pytest.mark.parametrize(
    "delta, expected",
    [
        (timedelta(seconds=5), "second"),
        (timedelta(minutes=2), "minute"),
        (timedelta(hours=3), "hour"),
        (timedelta(days=4), "day"),
    ],
)
def test_relative_time(delta, expected):
    now = datetime.now(timezone.utc)
    past = now - delta
    label = utils.relative_time(past)
    assert expected in label
