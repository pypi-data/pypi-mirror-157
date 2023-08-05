import datetime
import json
import subprocess
import os

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado


def _read_slurm_time(timestring: str) -> datetime.timedelta:
    # convert strings like "01:34:56" into a timedelta
    hr, min, sec = [int(x) for x in timestring.split(":")]
    return datetime.timedelta(hours=hr, minutes=min, seconds=sec)


def slurm_time_remaining(jobid: str) -> datetime.timedelta:
    total_elapsed = (
        subprocess.run(
            ["sacct", "-j", jobid, "-P", "--format", "time,elapsed", "--noheader"],
            capture_output=True,
        )
        .stdout.decode()
        .split()[0]
        .split("|")
    )
    total, elapsed = [_read_slurm_time(x) for x in total_elapsed]
    return total - elapsed


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        jobid = os.environ.get("SLURM_JOBID")
        if jobid:
            try:
                remaining = slurm_time_remaining(jobid)
                self.finish(
                    json.dumps(
                        {"data": {"remaining": remaining.seconds}, "error": None}
                    )
                )
            except Exception as e:
                self.finish(json.dumps({"data": None, "error": str(e)}))
        else:
            self.finish(json.dumps({"data": None, "error": "no jobid"}))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "slurm-time", "get_time")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
