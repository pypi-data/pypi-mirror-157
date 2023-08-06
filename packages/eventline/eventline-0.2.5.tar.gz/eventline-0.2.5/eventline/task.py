# Copyright (c) 2022 Exograd SAS.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
# IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from typing import Any, Optional, Dict

from eventline.api_object import ReadableAPIObject


class Task(ReadableAPIObject):
    """A task."""

    def __init__(self) -> None:
        super().__init__("task")

    def _read(self, data: Dict[str, Any]) -> None:
        self.id_ = self._read_string(data, "id")
        self.org_id = self._read_string(data, "org_id")
        self.project_id = self._read_string(data, "project_id")
        self.pipeline_id = self._read_string(data, "pipeline_id")
        self.pipeline_task = data["pipeline_task"]
        self.task_id = self._read_optional_string(data, "task_id")
        self.task_identities = self._read_string_array(data, "task_identities")
        self.spec = data["spec"]
        if "command_parameters" in data:
            self.spec = data["command_parameters"]
        self.instance_id = self._read_integer(data, "instance_id")
        self.status = self._read_string(data, "status")
        self.start_time = self._read_optional_datetime(data, "start_time")
        self.end_time = self._read_optional_datetime(data, "end_time")
        self.dependencies = self._read_string_array(data, "dependencies")
        self.failure_message = self._read_optional_string(
            data, "failure_message"
        )
        self.retry = self._read_optional_integer(data, "retry")
