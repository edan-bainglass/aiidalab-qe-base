import typing as t

import pytest
import traitlets as tl
from aiida import orm

from aiidalab_qe_base import mixins
from aiidalab_qe_base.models import Model

if t.TYPE_CHECKING:
    from .conftest import MockWorkChainNodeGenerator, StructureDataGenerator


def test_has_input_structure(generate_structure_data: "StructureDataGenerator"):
    class DummyModel(Model, mixins.HasInputStructure):
        pass

    model = DummyModel()
    assert not model.has_structure
    assert not model.has_pbc
    assert not model.has_tags

    structure = generate_structure_data()
    model.input_structure = structure
    assert model.has_structure
    assert model.has_pbc
    assert not model.has_tags

    structure.pbc = (False, False, False)
    assert not model.has_pbc

    structure = generate_structure_data(
        sites=[
            ("Si1", "Si", (0.0, 0.0, 0.0)),
            ("Si2", "Si", (1.923685, 1.110640, 0.785341)),
        ]
    )
    model.input_structure = structure
    assert model.has_tags


def test_has_model():
    class Child(Model):
        dependencies = ["b"]

        b = tl.Int()
        a = tl.Int(0)

    class Parent(Model, mixins.HasModels[Child]):
        b = tl.Int(5)

    parent = Parent()
    assert not parent.has_model("child")

    child = Child()
    parent.add_model("child", child)
    assert parent.has_model("child")
    assert parent.get_model("child") is child
    assert child.b == 5  # due to dependency link

    child1 = Child()
    child2 = Child()
    parent.add_models({"child1": child1, "child2": child2})
    assert parent.has_model("child1")
    assert parent.get_model("child1") is child1
    assert parent.has_model("child2")
    assert parent.get_model("child2") is child2

    with pytest.raises(KeyError):
        parent.get_model("nonexistent")


def test_has_process(generate_mock_workchain_node: "MockWorkChainNodeGenerator"):
    class DummyModel(mixins.HasProcess):
        x = tl.Int(0)

    model = DummyModel()
    assert not model.has_process

    process_node = generate_mock_workchain_node()
    model.process_uuid = process_node.uuid
    assert model.fetch_process_node() == process_node
    assert model.has_process
    assert "properties" in model.inputs
    assert model.properties == ["relax"]
    assert "structure" in model.outputs
    structure = model.outputs.structure
    assert isinstance(structure, orm.StructureData)
    assert len(structure.get_symbols_set()) == 1
    assert "Si" in structure.get_symbols_set()


def test_confirmable():
    class DummyModel(mixins.Confirmable):
        x = tl.Int(0)

    model = DummyModel()
    assert not model.confirmed
    model.confirm()
    assert model.confirmed
    model.x = 1
    assert not model.confirmed


def test_has_blockers():
    class DummyModel(mixins.HasBlockers):
        flag = tl.Bool(False)

        def _check_blockers(self):
            return ["blocked"] if self.flag else []

    model = DummyModel()
    assert not model.is_blocked
    model.update_blockers()
    assert model.blockers == []
    model.flag = True
    model.update_blockers()
    assert model.is_blocked
    model.update_blocker_messages()
    assert "blocked" in model.blocker_messages
