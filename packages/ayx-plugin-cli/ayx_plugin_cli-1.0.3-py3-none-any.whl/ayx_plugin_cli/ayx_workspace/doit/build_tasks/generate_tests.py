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
"""Task definition for generation of tests."""
import re
from typing import Dict

from ayx_plugin_cli.ayx_workspace.constants import AYX_CLI_TEMPLATES_PATH, AYX_WORKSPACE_JSON_PATH, BackendLanguage, TESTS_DIR
from ayx_plugin_cli.ayx_workspace.models.v1 import AyxWorkspaceV1

from jinja2 import Environment, FileSystemLoader


def task_generate_tests() -> Dict:
    """Generate tests for a specified tool."""
    return {
        "title": lambda task: "Generate tests",
        "actions": [
            generate_tests
        ],
        "file_dep": [AYX_WORKSPACE_JSON_PATH],
        "params": [
            {
                "name": "tool_name",
                "long": "tool_name",
                "type": str,
                "default": "PlaceholderToolName",
            },
            {
                "name": "tool_config",
                "long": "tool_config",
                "type": AyxWorkspaceV1,
                "default": AyxWorkspaceV1.load()
            }
        ],
        "uptodate": [False]
    }


def generate_tests(tool_name: str, tool_config: AyxWorkspaceV1) -> None:
    """Generate unit tests for a plugin."""
    def snake_case(name: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    template_path = AYX_CLI_TEMPLATES_PATH / tool_config.backend_language.value
    file_loader = FileSystemLoader(template_path)
    env = Environment(loader=file_loader)
    env.filters["snake_case"] = snake_case

    testfile_template = env.get_template("plugin_tests.j2")
    readme_template = env.get_template("README_tests.md")

    package_name = tool_config.tools[tool_name].backend.tool_module
    plugin_class = tool_config.tools[tool_name].backend.tool_class_name

    if tool_config.backend_language == BackendLanguage.Python:
        if not TESTS_DIR.exists():
            TESTS_DIR.mkdir(parents=True)

        input_anchors = {key: "pa.schema([])" for key in tool_config.tools[tool_name].configuration.input_anchors.keys()}
        output_anchors = {key: "pa.schema([])" for key in tool_config.tools[tool_name].configuration.output_anchors.keys()}
        testfile_template.stream(
            package_name=package_name,
            plugin_class=plugin_class,
            input_anchors=input_anchors,
            output_anchors=output_anchors,
            num_input_anchors=len(input_anchors),
            num_output_anchors=len(output_anchors),
            snake_case_plugin_name=snake_case(plugin_class) + "_plugin_service"
        ).dump(str((TESTS_DIR / f"test_{snake_case(plugin_class)}.py").resolve()))
        readme_template.stream().dump(str((TESTS_DIR / "README.md").resolve()))
        (TESTS_DIR / "__init__.py").touch(exist_ok=True)
        (TESTS_DIR.parent / "__init__.py").touch(exist_ok=True)
