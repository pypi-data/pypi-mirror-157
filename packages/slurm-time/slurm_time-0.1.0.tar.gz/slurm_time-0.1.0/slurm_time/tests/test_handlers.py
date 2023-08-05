import json
import pytest
from unittest import mock

import slurm_time.handlers


async def test_get_time_no_job(jp_fetch):
    # When
    response = await jp_fetch("slurm-time", "get_time")

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {"data": None, "error": "no jobid"}


async def test_get_time_jobid_no_slurm(jp_fetch, monkeypatch):
    monkeypatch.setenv("SLURM_JOBID", "none")
    response = await jp_fetch("slurm-time", "get_time")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["data"] == None


async def test_get_time(jp_fetch, monkeypatch):
    import subprocess

    class slurm_output:
        stdout = """00:05:00|00:00:39
        |00:00:39""".encode(
            "utf-8"
        )

    def mock_run(*args, **kwargs):
        return slurm_output

    monkeypatch.setenv("SLURM_JOBID", "444")
    monkeypatch.setattr(subprocess, "run", mock_run)
    response = await jp_fetch("slurm-time", "get_time")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["error"] == None
    assert payload["data"] == {"remaining": 261}
