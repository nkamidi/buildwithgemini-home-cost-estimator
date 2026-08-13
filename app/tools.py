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

import json
from typing import Any, Dict, List, Optional


# Regional Zip Code Database (Cost index & weather delay factors)
ZIP_DATABASE: Dict[str, Dict[str, Any]] = {
    "94102": {"city": "San Francisco, CA", "cost_multiplier": 1.65, "rain_days": 67, "snow_days": 0, "weather_delay_months": 1.0},
    "10001": {"city": "New York, NY", "cost_multiplier": 1.60, "rain_days": 120, "snow_days": 25, "weather_delay_months": 2.5},
    "90210": {"city": "Beverly Hills, CA", "cost_multiplier": 1.50, "rain_days": 35, "snow_days": 0, "weather_delay_months": 0.5},
    "80202": {"city": "Denver, CO", "cost_multiplier": 1.18, "rain_days": 85, "snow_days": 55, "weather_delay_months": 3.0},
    "30301": {"city": "Atlanta, GA", "cost_multiplier": 1.05, "rain_days": 110, "snow_days": 2, "weather_delay_months": 1.2},
    "75001": {"city": "Dallas, TX", "cost_multiplier": 1.00, "rain_days": 80, "snow_days": 1, "weather_delay_months": 1.0},
    "98101": {"city": "Seattle, WA", "cost_multiplier": 1.35, "rain_days": 155, "snow_days": 5, "weather_delay_months": 2.5},
    "60601": {"city": "Chicago, IL", "cost_multiplier": 1.28, "rain_days": 122, "snow_days": 38, "weather_delay_months": 3.0},
}


def get_zip_info(zip_code: str) -> str:
    """Retrieves regional cost index multipliers and historical weather patterns (rain/snow days) for a given zip code.

    Args:
        zip_code: 5-digit US ZIP code (e.g. '94102', '10001', '80202').

    Returns:
        JSON string containing city name, cost multiplier, and weather delay indicators.
    """
    z = zip_code.strip()
    if z in ZIP_DATABASE:
        return json.dumps(ZIP_DATABASE[z], indent=2)
    
    # Generic regional fallback
    return json.dumps({
        "city": f"ZIP {z} Region",
        "cost_multiplier": 1.12,
        "rain_days": 90,
        "snow_days": 10,
        "weather_delay_months": 1.5,
        "note": "Estimated using national regional baseline."
    }, indent=2)


def calculate_home_estimate(
    total_budget: float,
    sqft: float,
    stories: str = "two-story",
    is_sloped: bool = False,
    slope_degrees: float = 0.0,
    bedrooms: int = 3,
    bathrooms: int = 2,
    garages: int = 2,
    additional_rooms: Optional[List[str]] = None,
    appliance_tier: str = "premium",
    flooring_type: str = "hardwood",
    roofing_type: str = "asphalt_shingle",
    zip_code: str = "75001"
) -> str:
    """Calculates comprehensive custom home construction cost breakdown, value engineering recommendations, and weather-adjusted timeline.

    Args:
        total_budget: User's target maximum budget in USD (e.g. 750000).
        sqft: Total interior square footage (e.g. 2800).
        stories: 'single-story', 'two-story', or 'multi-story'.
        is_sloped: True if the building plot is sloped; False if flat.
        slope_degrees: Angle of slope in degrees if land is sloped (e.g. 15.0).
        bedrooms: Number of bedrooms.
        bathrooms: Number of bathrooms.
        garages: Garage car bays (e.g. 2 or 3).
        additional_rooms: List of extra rooms (e.g. ['home_office', 'gym']).
        appliance_tier: 'regular', 'premium', or 'industrial'.
        flooring_type: 'carpet', 'lvt', 'tile', 'hardwood', or 'polished_concrete'.
        roofing_type: 'asphalt_shingle', 'metal', 'clay_tile', or 'slate'.
        zip_code: 5-digit ZIP code for regional cost and weather multipliers.

    Returns:
        JSON report with itemized cost breakdown, budget analysis, value engineering suggestions, and timeline estimates.
    """
    z_data = json.loads(get_zip_info(zip_code))
    mult = z_data["cost_multiplier"]

    # 1. Land Preparation / Grading Costs
    if not is_sloped or slope_degrees <= 0:
        land_prep_cost = (5000.0 + (sqft * 2.5)) * mult
    else:
        # Sloped land requires extra excavation, retaining walls, and soil stabilization
        land_prep_cost = (10000.0 + (slope_degrees * 1500.0) + (sqft * 14.0)) * mult

    # 2. Structural Framing / Base Shell
    story_rates = {
        "single-story": 125.0,
        "two-story": 145.0,
        "multi-story": 170.0
    }
    base_rate = story_rates.get(stories.lower(), 145.0)
    structure_cost = (sqft * base_rate) * mult

    # 3. Layout / Rooms & Garages
    layout_cost = (
        (bedrooms * 14000.0) +
        (bathrooms * 24000.0) +
        (garages * 22000.0)
    ) * mult

    extra_room_cost = 0.0
    if additional_rooms:
        extra_room_cost = len(additional_rooms) * 18000.0 * mult

    # 4. Finishes (Appliances, Flooring, Roofing)
    appliance_costs = {"regular": 6000.0, "premium": 18000.0, "industrial": 42000.0}
    flooring_rates = {"carpet": 4.5, "lvt": 7.5, "tile": 12.0, "hardwood": 16.5, "polished_concrete": 11.0}
    roofing_rates = {"asphalt_shingle": 6.5, "metal": 13.0, "clay_tile": 19.0, "slate": 29.0}

    app_cost = appliance_costs.get(appliance_tier.lower(), 18000.0) * mult
    floor_cost = (sqft * flooring_rates.get(flooring_type.lower(), 16.5)) * mult
    roof_cost = (sqft * 0.7 * roofing_rates.get(roofing_type.lower(), 6.5)) * mult  # Roof footprint approx 0.7 sqft

    finishes_cost = app_cost + floor_cost + roof_cost

    # Subtotals
    subtotal = land_prep_cost + structure_cost + layout_cost + extra_room_cost + finishes_cost

    # Material vs Labor Split (approx 45% Material, 55% Labor)
    material_cost = subtotal * 0.45
    labor_cost = subtotal * 0.55

    total_calculated_cost = subtotal

    # Budget Check & Value Engineering
    budget_delta = total_calculated_cost - total_budget
    is_over_budget = budget_delta > 0

    value_engineering = []
    if is_over_budget:
        # Generate smart compromises
        if roofing_type.lower() in ["slate", "clay_tile"]:
            savings = (roofing_rates[roofing_type.lower()] - roofing_rates["asphalt_shingle"]) * sqft * 0.7 * mult
            value_engineering.append(f"Switch roofing from {roofing_type.title()} to Architectural Asphalt Shingle (Saves ~${savings:,.2f})")
        
        if appliance_tier.lower() == "industrial":
            savings = (appliance_costs["industrial"] - appliance_costs["premium"]) * mult
            value_engineering.append(f"Downgrade appliances from Industrial/High-End to Premium Chef Tier (Saves ~${savings:,.2f})")

        if flooring_type.lower() in ["hardwood", "tile"]:
            savings = (flooring_rates[flooring_type.lower()] - flooring_rates["lvt"]) * sqft * mult
            value_engineering.append(f"Replace {flooring_type.title()} flooring with Luxury Vinyl Tile (LVT) (Saves ~${savings:,.2f})")

        if is_sloped and slope_degrees > 10:
            value_engineering.append(f"Consider stepped-foundation design to reduce heavy hillside excavation grading fees.")

    # Construction Timeline Estimation (Months)
    base_duration_months = 7.0 + (sqft / 450.0)
    weather_delay = z_data.get("weather_delay_months", 1.5)
    total_timeline_months = round(base_duration_months + weather_delay, 1)

    result = {
        "budget": total_budget,
        "zip_code": zip_code,
        "city_region": z_data["city"],
        "total_estimated_cost": round(total_calculated_cost, 2),
        "budget_status": {
            "status": "OVER_BUDGET" if is_over_budget else "WITHIN_BUDGET",
            "variance": round(budget_delta, 2),
            "summary": f"Estimate is ${abs(budget_delta):,.2f} {'OVER' if is_over_budget else 'UNDER'} budget."
        },
        "cost_breakdown": {
            "land_preparation": round(land_prep_cost, 2),
            "building_structure": round(structure_cost + layout_cost + extra_room_cost, 2),
            "material": round(material_cost, 2),
            "labor": round(labor_cost, 2),
            "finishes": round(finishes_cost, 2)
        },
        "value_engineering_recommendations": value_engineering if is_over_budget else ["Selections fit comfortably within budget!"],
        "timeline_estimate": {
            "base_construction_months": round(base_duration_months, 1),
            "weather_delay_months": weather_delay,
            "total_duration_months": total_timeline_months,
            "weather_notes": f"Includes estimated delays for {z_data['rain_days']} rain days & {z_data['snow_days']} snow/freeze days in {z_data['city']}."
        },
        "ui_quick_choices": [
            "[Adjust Budget]",
            "[Apply Value Engineering Suggestions]",
            "[Explore Roofing/Flooring Alternatives]",
            "[Generate PDF Cost Breakdown Card]"
        ]
    }

    return json.dumps(result, indent=2)
