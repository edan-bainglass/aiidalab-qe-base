from aiidalab_qe_base import models


def test_code_model(default_user_email, pw_code):
    model = models.CodeModel(
        name="pw",
        description="Quantum ESPRESSO pw.x",
        default_calc_job_plugin="quantumespresso.pw",
    )

    assert model.options == []
    assert model.selected is None

    model.update(user_email=default_user_email)

    assert model.options
    assert model.first_option == pw_code.uuid
    assert model.selected == pw_code.uuid

    state = model.get_model_state()
    assert state["code"] == pw_code.uuid
    assert state["nodes"] == 1
    assert state["cpus"] == 1

    model.set_model_state({"code": "does-not-exist", "nodes": 2, "cpus": 3})
    assert model.selected is None
    assert model.num_nodes == 2
    assert model.num_cpus == 3


def test_pw_code_model(default_user_email, pw_code):
    model = models.PwCodeModel()
    model.update(user_email=default_user_email)

    state = model.get_model_state()
    assert state["parallelization"] == {}

    model.parallelization_override = True
    model.npool = 4
    state = model.get_model_state()
    assert state["parallelization"] == {"npool": 4}

    model.set_model_state({"parallelization": {"npool": 8}})
    assert model.parallelization_override
    assert model.npool == 8
