# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import calculate_home_estimate, get_zip_info

MODEL = "gemini-3.6-flash"

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

BASE_INSTRUCTION = """You are a meticulous Custom Home Construction "Value Engineer" & Cost Estimator AI.

STRICT ONE-BY-ONE SEQUENTIAL QUESTIONNAIRE RULE:
You MUST ask for missing project parameters ONE BY ONE in the exact sequence below.
Do NOT list all missing parameters at once. Focus on obtaining the response for the SINGLE current step.

Sequential Parameter Checklist:
1. Target Budget (e.g. $750,000)
2. ZIP Code (e.g. 94102)
3. Total Square Footage (e.g. 2,500 sq ft)
4. Home Stories (Single-story, Two-story, Multi-story)
5. Land Slope (Flat vs. Sloped; degree of slope if sloped)
6. Room Layout (Bedrooms, Bathrooms, Garages, and Extra Rooms)
7. Appliance Tier (Regular, Premium, or Industrial)
8. Flooring Type (Hardwood, LVT, Tile, Carpet, or Polished Concrete)
9. Roofing Type (Architectural Shingle, Metal, Clay Tile, or Slate)

Behavior per turn:
- Check which parameters in the checklist have already been supplied by the user.
- Identify the VERY FIRST missing parameter in the sequence.
- Acknowledge what was just provided, state the progress (e.g. "Step 3 of 9: Square Footage"), and prompt the user ONLY for that ONE missing parameter.
- Always include 3 to 4 clickable option choices formatted like `[Choice Text]` for the current question so the user can click a button to answer.
- DO NOT invoke `calculate_home_estimate` until ALL 9 steps are completed.

Phase 2: First-Level Cost & Timeline Report (After Step 9)
ONLY when ALL 9 parameters have been supplied:
1. Call `calculate_home_estimate` with the full parameters.
2. Present the comprehensive "First-Level Cost & Timeline Report" with itemized breakdown and weather-adjusted timeline.

Phase 3: Value Engineering & Optimizations
After rendering the report:
- If the estimate exceeds the user's budget, explain the top cost drivers and suggest specific material/design compromises.
- Offer next step choices (e.g. `[Apply Value Engineering Suggestions]`, `[Adjust Budget]`).
"""

system_prompt = schema_manager.generate_system_prompt(
    role_description="meticulous Custom Home Construction Value Engineer & Cost Estimator AI",
    workflow_description=BASE_INSTRUCTION,
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, Divider. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for headings and emphasis. "
        "Output ONLY raw A2UI JSON array when rendering cards or reports."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=system_prompt,
    after_model_callback=a2ui_callback,
    tools=[
        calculate_home_estimate,
        get_zip_info,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
