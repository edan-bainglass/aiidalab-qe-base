from __future__ import annotations

import typing as t

import pytest
from aiida import engine, orm
from aiida.engine.utils import instantiate_process
from aiida.manage import Profile, get_manager

pytest_plugins = ["aiida.tools.pytest_fixtures"]


class MockWorkChain(engine.WorkChain):
    @classmethod
    def define(cls, spec: engine.processes.workchains.workchain.WorkChainSpec):
        super().define(spec)
        spec.input("properties", valid_type=orm.List)
        spec.output("structure", valid_type=orm.StructureData)


@pytest.fixture
def default_user_email(aiida_profile: Profile) -> str:
    """Generates the default user's email."""
    return orm.User.collection.get_default().email


class InstalledCodeFactory(t.Protocol):
    def __call__(
        self,
        label: str | None = ...,
        description: str | None = ...,
        default_calc_job_plugin: str | None = ...,
        computer: orm.Computer = ...,
        filepath_executable: str = ...,
        use_double_quotes: bool = ...,
        with_mpi: bool | None = ...,
        prepend_text: str = ...,
        append_text: str = ...,
    ) -> orm.InstalledCode: ...


@pytest.fixture
def pw_code(aiida_code_installed: InstalledCodeFactory) -> orm.InstalledCode:
    """Generates an installed PW code."""
    return aiida_code_installed(
        label="pw",
        default_calc_job_plugin="quantumespresso.pw",
    )


class StructureDataGenerator(t.Protocol):
    def __call__(
        self,
        name: str = "silicon",
        pbc: tuple[bool, bool, bool] = (True, True, True),
        cell: list[list[float]] | None = None,
        sites: list[tuple[str, str, tuple[float, float, float]]] | None = None,
    ) -> orm.StructureData: ...


@pytest.fixture
def generate_structure_data() -> StructureDataGenerator:
    """Generates a `StructureData` instance.

    Predefined structures (cell and sites) can be selected with the `name` parameter:
    - Bulk silicon
    - Bulk silica (SiO2)
    - Water molecule (H2O)

    Predefined cell/sites can still be overwritten, for example, a water molecule with
    a larger cell, or a tagged structure.

    Parameters
    ----------
    `name`: `str`
        Name of the structure.
    `pbc`: `tuple[bool, bool, bool]`
        Periodic boundary conditions.
    `cell`: `list[list[float]] | None`
        Cell parameters.
    `sites`: `list[tuple[str, str, tuple[float, float, float]]] | None`
        Atomic sites given as tuples of (name, symbol, position).

    Returns
    -------
    `StructureData`
        The generated `StructureData` instance.
    """

    def _generate_structure_data(
        name="silicon",
        pbc: tuple[bool, bool, bool] = (True, True, True),
        cell: list[list[float]] | None = None,
        sites: list[tuple[str, str, tuple[float, float, float]]] | None = None,
    ):
        if name == "silicon":
            cell = cell or [
                [3.84737, 0.0, 0.0],
                [1.923685, 3.331920, 0.0],
                [1.923685, 1.110640, 3.141364],
            ]
            sites = sites or [
                ("Si", "Si", (0.0, 0.0, 0.0)),
                ("Si", "Si", (1.923685, 1.110640, 0.785341)),
            ]

        elif name == "silica":
            cell = cell or [
                [4.18, 0.0, 0.0],
                [0.0, 4.18, 0.0],
                [0.0, 0.0, 2.66],
            ]
            sites = sites or [
                ("Si", "Si", (0.0, 0.0, 0.0)),
                ("Si", "Si", (2.09, 2.09, 1.33)),
                ("O", "O", (0.81, 3.37, 1.33)),
                ("O", "O", (1.28, 1.28, 0.0)),
                ("O", "O", (2.9, 2.9, 0.0)),
                ("O", "O", (0.81, 3.37, 1.33)),
            ]

        elif name == "water":
            cell = cell or [
                [10.0, 0.0, 0.0],
                [0.0, 10.0, 0.0],
                [0.0, 0.0, 10.0],
            ]
            sites = sites or [
                ("H", "H", (0.0, 0.0, 0.0)),
                ("O", "O", (0.0, 0.0, 1.0)),
                ("H", "H", (0.0, 1.0, 0.0)),
            ]

        assert cell, "Cell is not defined"
        assert sites, "Sites are not defined"

        structure = orm.StructureData(cell=cell)
        for kind_name, symbol, position in sites:
            structure.append_atom(
                name=kind_name,
                symbols=symbol,
                position=position,
            )

        structure.pbc = pbc

        return structure

    return _generate_structure_data


class WorkChainGenerator(t.Protocol):
    def __call__(
        self,
        process_class: engine.WorkChain,
        inputs: dict,
    ) -> engine.WorkChain: ...


@pytest.fixture
def generate_workchain() -> WorkChainGenerator:
    """Generates a `WorkChain` instance."""

    def _generate_workchain(
        process_class: engine.WorkChain,
        inputs: dict,
    ) -> engine.WorkChain:
        runner = get_manager().get_runner()
        process = instantiate_process(runner, process_class, **inputs)
        return t.cast(engine.WorkChain, process)

    return _generate_workchain


class MockWorkChainNodeGenerator(t.Protocol):
    def __call__(self) -> orm.WorkChainNode: ...


@pytest.fixture
def generate_mock_workchain_node(
    generate_workchain: WorkChainGenerator,
    generate_structure_data: StructureDataGenerator,
) -> MockWorkChainNodeGenerator:
    """Generates a mock `WorkChainNode` instance."""

    mock_structure = generate_structure_data()
    mock_structure.store()

    def _generate_mock_workchain_node() -> orm.WorkChainNode:
        workchain = generate_workchain(MockWorkChain, {"properties": ["relax"]})
        workchain.out("structure", mock_structure)
        workchain.update_outputs()
        return workchain.node

    return _generate_mock_workchain_node
