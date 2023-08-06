# Copyright (C) 2022 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Task definition for creating a language-specific backend artifact for the workspace."""
from pathlib import Path
from typing import Any, Dict, Generator, List

from ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_ARTIFACT_EXTENSIONS,
    BUILD_CACHE_DIR,
    BackendLanguage,
    TEMPLATE_TOOL_UI_DIR,
)
from ayx_plugin_cli.ayx_workspace.models.v1 import AyxWorkspaceV1
from ayx_plugin_cli.node_js_helpers import run_npm


def generate_artifact_actions(
    workspace: AyxWorkspaceV1, backend_artifact_path: Path
) -> List[Any]:
    """Generate the list of actions that generate UI and backend artifacts."""
    all_tools = [tool.backend.tool_class_name for _, tool in workspace.tools.items()]
    return [
        lambda: print(f"Creating {workspace.name}.yxi..."),
        (_build_action, [all_tools]),
        generate_build_artifact_command(
            workspace.backend_language, BUILD_CACHE_DIR, backend_artifact_path
        ),
    ]


def generate_build_artifact_command(
    language: BackendLanguage, cache_dir: Path, output_path: Path
) -> List[str]:
    """Delegate call to backend's build artifact command."""
    try:
        return {
            BackendLanguage.Python: [
                "ayx_python_sdk",
                "build-artifact",
                "--dependency-cache-dir",
                str(cache_dir.resolve()),
                "--output-path",
                str(output_path.resolve()),
            ]
        }[language]
    except KeyError:
        raise NotImplementedError(f"{language} is not supported as a backend language.")


def _build_action(all_tools: List[str]) -> None:
    for tool_name in all_tools:
        ui_dir = TEMPLATE_TOOL_UI_DIR % {"tool_name": tool_name}
        completed_process = run_npm(["install"], cwd=Path(".") / ui_dir,)
        if completed_process.returncode != 0:
            raise RuntimeError(
                f"'npm install' on directory {ui_dir} failed with:\n"
                f"stdout:\n{completed_process.stdout}\n\n"
                f"stderr:{completed_process.stderr}"
            )
        completed_process = run_npm(["run", "build"], cwd=Path(".") / ui_dir,)

        if completed_process.returncode != 0:
            raise RuntimeError(
                f"'npm run build' on directory {ui_dir} failed with:\n"
                f"stdout:\n{completed_process.stdout}\n\n"
                f"stderr:{completed_process.stderr}"
            )


def task_generate_artifact() -> Generator[Dict, None, None]:
    """Create a language-specific backend artifact from the tools in the workspace."""
    workspace = AyxWorkspaceV1.load()
    backend_artifact_path = Path(
        "main" + AYX_WORKSPACE_ARTIFACT_EXTENSIONS[workspace.backend_language]
    )

    yield {
        "task_dep": ["generate_config_files"],
        "actions": generate_artifact_actions(workspace, backend_artifact_path),
        "targets": [backend_artifact_path],
        "clean": True,
        "name": "build_artifacts",
    }
