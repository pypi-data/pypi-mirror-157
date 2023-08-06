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
"""Task definition for creating a YXI for the workspace."""
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Generator

from ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_ARTIFACT_EXTENSIONS,
    AYX_WORKSPACE_JSON_PATH,
    TEMPLATE_TOOL_CONFIG_DIR,
    TEMPLATE_TOOL_UI_DIR,
    WORKSPACE_CONFIG_DIR,
    YXI_OUTPUT_DIR,
)
from ayx_plugin_cli.ayx_workspace.models.v1 import (
    AyxWorkspaceV1,
    ToolSettingsV1,
)


def task_create_yxi() -> Generator[Dict, None, None]:
    """Create a YXI from the tools in the workspace."""
    workspace = AyxWorkspaceV1.load()
    backend_artifact_path = Path(
        "main" + AYX_WORKSPACE_ARTIFACT_EXTENSIONS[workspace.backend_language]
    )

    yield {
        "file_dep": [backend_artifact_path, AYX_WORKSPACE_JSON_PATH],
        "task_dep": ["generate_config_files", "generate_artifact"],
        "actions": [(create_yxi, [workspace, backend_artifact_path])],
        "targets": [YXI_OUTPUT_DIR / f"{workspace.name}.yxi"],
        "clean": True,
        "name": "create_yxi",
    }


def create_yxi(workspace: AyxWorkspaceV1, backend_artifact_path: Path) -> None:
    """Bundle workspace tools into a yxi."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        copy_top_level_files(workspace, temp_dir_path)
        for _, tool in workspace.tools.items():
            copy_tool(tool, temp_dir_path)

        make_archive(backend_artifact_path, workspace, temp_dir_path)


def copy_top_level_files(workspace: AyxWorkspaceV1, temp_dir: Path) -> None:
    """Copy top-level config xml and icon files from workspace directory into temp directory for yxi creation."""
    top_level_config = WORKSPACE_CONFIG_DIR / "Config.xml"
    shutil.copy(top_level_config, temp_dir)
    shutil.copy(workspace.package_icon_path, temp_dir)


def copy_tool(tool: ToolSettingsV1, temp_dir: Path) -> None:
    """Copy tool files from workspace directory into temp directory for yxi creation."""
    tool_name = tool.backend.tool_class_name
    tool_config_dir = Path(TEMPLATE_TOOL_CONFIG_DIR % {"tool_name": tool_name})
    tool_schemas_dir = Path("DcmSchemas") / tool_name
    tool_config_file = tool_config_dir / f"{tool_name}Config.xml"
    tool_config_icon = Path(tool.configuration.icon_path).resolve()

    manifest_json = tool_config_dir / "manifest.json"

    tool_folder = temp_dir / tool_name
    tool_folder.mkdir()
    shutil.copy(tool_config_file, tool_folder)
    if tool_schemas_dir.exists():
        shutil.copytree(tool_schemas_dir, tool_folder / "DcmSchemas", dirs_exist_ok=True)
    shutil.copy(manifest_json, tool_folder)
    shutil.copy(tool_config_icon, tool_folder)

    tool_ui_artifact_dir = (
        Path(".") / (TEMPLATE_TOOL_UI_DIR % {"tool_name": tool_name}) / "dist"
    )
    for path in tool_ui_artifact_dir.iterdir():
        if path.is_file() and path.suffix != ".gz":
            shutil.copy(path, tool_folder)


def make_archive(
    artifact_path: Path, workspace: AyxWorkspaceV1, temp_dir: Path
) -> None:
    """Zip workspace and rename to yxi file."""
    YXI_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy(artifact_path, Path(temp_dir) / list(workspace.tools)[0])
    shutil.make_archive(f"{workspace.name}.yxi", "zip", temp_dir)
    shutil.move(f"{workspace.name}.yxi.zip", YXI_OUTPUT_DIR / f"{workspace.name}.yxi")
