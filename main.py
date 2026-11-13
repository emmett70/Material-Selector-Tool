from dataclasses import dataclass
from drafter import *
from bakery import assert_equal


set_site_information(
    "Emmett Nilsson",
    "An interactive tool to compare and select engineering materials.",
    [],
    [],
    [],
)


@dataclass
class Material:
    """
    Represents an engineering material and its core physical and economic properties.

    Attributes:
        name (str): The common name of the material.
        strength (float): Tensile strength measured in megapascals (MPa).
        density (float): Mass per unit volume measured in g/cm^3.
        relative_cost (float): Cost rating on a 1.0 (cheapest) to 10.0 (most expensive) scale.
        best_for (str): Primary engineering applications suited for this material.
        description (str): Brief summary of the material's trade-offs for beginners.
    """
    name: str
    strength: float
    density: float
    relative_cost: float
    best_for: str
    description: str


@dataclass
class State:
    """
    Maintains persistent user selections and material data across all website routes.

    Attributes:
        materials (list[Material]): Complete catalog of available engineering materials.
        selected_application (str): The application chosen by the user.
        priorities (list[str]): List of material properties prioritized by the user.
        recommended_materials (list[Material]): Materials matching user preferences.
        selected_material_name (str): Name of the material currently being inspected.
        status_message (str): Feedback message for searches or empty results.
    """
    materials: list[Material]
    selected_application: str
    priorities: list[str]
    recommended_materials: list[Material]
    selected_material_name: str
    status_message: str


def build_default_materials() -> list[Material]:
    """
    Creates and returns the initial catalog of common engineering materials.

    Returns:
        list[Material]: A list of predefined Material dataclass instances.
    """
    return [
        Material(
            "Aluminum 6061",
            310.0,
            2.70,
            3.5,
            "Bicycle Frame",
            "Lightweight, corrosion-resistant, and affordable metal used in frames.",
        ),
        Material(
            "Structural Steel",
            400.0,
            7.85,
            2.0,
            "Bridge Support",
            "Very strong and inexpensive, though heavy and prone to rust if uncoated.",
        ),
        Material(
            "Titanium Alloy",
            900.0,
            4.43,
            8.5,
            "Aerospace Bracket",
            "Exceptional strength-to-weight ratio and corrosion resistance, but costly.",
        ),
        Material(
            "ABS Plastic",
            40.0,
            1.04,
            1.5,
            "Phone Case",
            "Impact-resistant, very lightweight, and cheap to mold for consumer goods.",
        ),
        Material(
            "Carbon Fiber",
            1500.0,
            1.60,
            9.5,
            "Bicycle Frame",
            "Ultra-high strength and very low density, but expensive and brittle on impact.",
        ),
        Material(
            "Polycarbonate",
            65.0,
            1.20,
            2.5,
            "Phone Case",
            "Tough, transparent polymer with strong impact resistance at moderate cost.",
        ),
    ]


def calculate_material_score(material: Material, application: str, priorities: list[str]) -> float:
    """
    Calculates a suitability score for a material based on user application and priorities.

    Args:
        material (Material): The material being evaluated.
        application (str): The target engineering application.
        priorities (list[str]): Properties prioritized by the user.

    Returns:
        float: A numerical score indicating how well the material fits the criteria.
    """
    score = 0.0
    if material.best_for == application:
        score += 3.0
    if "High Strength" in priorities and material.strength >= 300.0:
        score += 2.5
    if "Low Density" in priorities and material.density <= 3.0:
        score += 2.5
    if "Low Cost" in priorities and material.relative_cost <= 3.5:
        score += 2.5
    return score


def explain_match(material: Material, application: str, priorities: list[str]) -> str:
    """
    Generates a plain-English explanation of why a material fits the user's criteria.

    Args:
        material (Material): The recommended material.
        application (str): The target engineering application.
        priorities (list[str]): Properties prioritized by the user.

    Returns:
        str: A readable summary of the material's matching strengths.
    """
    reasons: list[str] = []
    if material.best_for == application:
        reasons.append("Ideal for " + application)
    if "High Strength" in priorities and material.strength >= 300.0:
        reasons.append("High tensile strength")
    if "Low Density" in priorities and material.density <= 3.0:
        reasons.append("Lightweight")
    if "Low Cost" in priorities and material.relative_cost <= 3.5:
        reasons.append("Budget-friendly")

    if len(reasons) == 0:
        return "General match"
    return ", ".join(reasons)


def find_material_by_name(materials: list[Material], target_name: str) -> Material | None:
    """
    Searches the material list for a material matching the given name (case-insensitive).

    Args:
        materials (list[Material]): The list of available materials.
        target_name (str): The name entered or selected by the user.

    Returns:
        Material | None: The matching Material instance, or None if not found.
    """
    cleaned_target = target_name.strip().lower()
    for item in materials:
        if item.name.lower() == cleaned_target:
            return item
    return None


@route
def index(state: State) -> Page:
    """
    Displays the welcome home page for the Material Selector Tool.

    Args:
        state (State): The current application state.

    Returns:
        Page: The rendered home page with a button to start selecting materials.
    """
    return Page(
        state,
        [
            Header("Engineering Material Selector Tool"),
            Text("Compare common engineering materials by strength, density, and cost."),
            Text("Designed for students learning the trade-offs of material selection."),
            Button("Start Material Selection", select_application),
            Button("View All Materials", compare_materials),
        ],
    )


@route
def select_application(state: State) -> Page:
    """
    Allows the user to select an engineering application from a dropdown menu.

    Args:
        state (State): The current application state.

    Returns:
        Page: The application selection page.
    """
    applications = [
        "Bicycle Frame",
        "Phone Case",
        "Bridge Support",
        "Aerospace Bracket",
    ]
    return Page(
        state,
        [
            Header("Step 1: Choose an Application"),
            Text("What will this material be used for?"),
            SelectBox("chosen_app", applications, state.selected_application),
            Button("Continue to Preferences", select_preferences),
            Button("Back to Home", index),
        ],
    )


@route
def select_preferences(state: State, chosen_app: str) -> Page:
    """
    Saves the chosen application and lets the user pick priority properties via checkboxes.

    Args:
        state (State): The current application state.
        chosen_app (str): The application selected on the previous page.

    Returns:
        Page: The property preferences selection page.
    """
    state.selected_application = chosen_app
    has_strength = "High Strength" in state.priorities
    has_density = "Low Density" in state.priorities
    has_cost = "Low Cost" in state.priorities

    return Page(
        state,
        [
            Header("Step 2: Select Important Properties"),
            Text("Application selected: " + state.selected_application),
            Text("Check the material properties that matter most for your design:"),
            CheckBox("want_strength", has_strength),
            Text("High Strength (300+ MPa tensile strength)"),
            CheckBox("want_density", has_density),
            Text("Low Density (3.0 g/cm^3 or lighter)"),
            CheckBox("want_cost", has_cost),
            Text("Low Cost (3.5 or lower relative cost rating)"),
            Button("Submit Preferences", show_results),
            Button("Change Application", select_application),
        ],
    )


@route
def show_results(
    state: State,
    want_strength: bool,
    want_density: bool,
    want_cost: bool,
) -> Page:
    """
    Evaluates all materials against user preferences and displays a clean results table.

    Args:
        state (State): The current application state.
        want_strength (bool): Whether the user prioritized high strength.
        want_density (bool): Whether the user prioritized low density.
        want_cost (bool): Whether the user prioritized low cost.

    Returns:
        Page: The recommendations page with a formatted table and search options.
    """
    updated_priorities: list[str] = []
    if want_strength:
        updated_priorities.append("High Strength")
    if want_density:
        updated_priorities.append("Low Density")
    if want_cost:
        updated_priorities.append("Low Cost")
    state.priorities = updated_priorities

    matches: list[Material] = []
    for item in state.materials:
        score = calculate_material_score(item, state.selected_application, state.priorities)
        if score >= 2.5:
            matches.append(item)

    state.recommended_materials = matches

    content: list[Component] = [
        Header("Recommended Materials"),
        Text("Selected Application: " + state.selected_application),
    ]

    if len(state.priorities) > 0:
        content.append(Text("Selected Priorities: " + ", ".join(state.priorities)))
    else:
        content.append(Text("Selected Priorities: None (showing best matches for application)"))

    if len(state.recommended_materials) == 0:
        state.status_message = "No exact matches found. Try selecting fewer priorities or view all materials."
        content.append(Text(state.status_message))
    else:
        state.status_message = "Found " + str(len(state.recommended_materials)) + " matching material(s):"
        content.append(Text(state.status_message))

        result_rows: list[list[str]] = [
            ["Material", "Strength (MPa)", "Density (g/cm^3)", "Cost (1-10)", "Why It Fits"]
        ]
        for mat in state.recommended_materials:
            why_text = explain_match(mat, state.selected_application, state.priorities)
            result_rows.append(
                [
                    mat.name,
                    str(mat.strength),
                    str(mat.density),
                    str(mat.relative_cost),
                    why_text,
                ]
            )
        content.append(Table(result_rows))

    content.append(Header("Inspect a Specific Material"))
    content.append(Text("Enter a material name from the table above to view its full summary:"))
    content.append(TextBox("search_name", state.selected_material_name))
    content.append(Button("View Material Details", material_details))
    content.append(Button("Compare All Materials", compare_materials))
    content.append(Button("Start Over", reset_selector))

    return Page(state, content)


@route
def material_details(state: State, search_name: str) -> Page:
    """
    Displays detailed engineering properties for a searched material name.

    Args:
        state (State): The current application state.
        search_name (str): The name of the material entered by the user.

    Returns:
        Page: A detail page showing properties or an error message if not found.
    """
    state.selected_material_name = search_name
    found = find_material_by_name(state.materials, search_name)

    if found is None:
        state.status_message = "Material '" + search_name + "' was not found in the database."
        return Page(
            state,
            [
                Header("Material Not Found"),
                Text(state.status_message),
                Text(
                    "Available materials: Aluminum 6061, Structural Steel, Titanium Alloy, "
                    "ABS Plastic, Carbon Fiber, Polycarbonate."
                ),
                Button("Compare All Materials", compare_materials),
                Button("Start Over", reset_selector),
            ],
        )

    state.status_message = "Viewing details for " + found.name
    return Page(
        state,
        [
            Header("Material Details: " + found.name),
            Text("Tensile Strength: " + str(found.strength) + " MPa"),
            Text("Density: " + str(found.density) + " g/cm^3"),
            Text("Relative Cost Rating: " + str(found.relative_cost) + " / 10.0"),
            Text("Ideal Application: " + found.best_for),
            Text("Engineering Summary: " + found.description),
            Button("Compare All Materials", compare_materials),
            Button("Start Over", reset_selector),
        ],
    )


@route
def compare_materials(state: State) -> Page:
    """
    Displays a side-by-side comparison table of all materials in the database.

    Args:
        state (State): The current application state.

    Returns:
        Page: A comparison table page of all materials and their properties.
    """
    rows: list[list[str]] = [
        ["Material", "Strength (MPa)", "Density (g/cm^3)", "Cost (1-10)", "Best Application"]
    ]
    for item in state.materials:
        rows.append(
            [
                item.name,
                str(item.strength),
                str(item.density),
                str(item.relative_cost),
                item.best_for,
            ]
        )

    return Page(
        state,
        [
            Header("Full Material Property Comparison"),
            Text("Compare all available materials side-by-side:"),
            Table(rows),
            Button("Select an Application", select_application),
            Button("Start Over", reset_selector),
        ],
    )


@route
def reset_selector(state: State) -> Page:
    """
    Resets all user selections and recommendations back to default values.

    Args:
        state (State): The current application state.

    Returns:
        Page: Redirects to the home page with a freshly reset state.
    """
    state.selected_application = "Bicycle Frame"
    state.priorities = []
    state.recommended_materials = []
    state.selected_material_name = ""
    state.status_message = "Selections have been reset."
    return index(state)


# ---------------------------------------------------------------------------
# Unit Tests for Helper Functions and All Routes
# ---------------------------------------------------------------------------

def make_test_state() -> State:
    """
    Creates a fresh State instance for deterministic unit testing.

    Returns:
        State: A default State initialized with standard materials.
    """
    return State(
        materials=build_default_materials(),
        selected_application="Bicycle Frame",
        priorities=[],
        recommended_materials=[],
        selected_material_name="",
        status_message="",
    )


# Helper function unit tests
assert_equal(len(build_default_materials()), 6)
assert_equal(
    calculate_material_score(build_default_materials()[0], "Bicycle Frame", ["High Strength"]),
    5.5,
)
assert_equal(
    explain_match(build_default_materials()[0], "Bicycle Frame", ["High Strength"]),
    "Ideal for Bicycle Frame, High tensile strength",
)
assert_equal(find_material_by_name(build_default_materials(), "abs plastic").name, "ABS Plastic")
assert_equal(find_material_by_name(build_default_materials(), "Unobtainium"), None)

# Route 1: index
test_state_1 = make_test_state()
assert_equal(isinstance(index(test_state_1), Page), True)

# Route 2: select_application
test_state_2 = make_test_state()
assert_equal(isinstance(select_application(test_state_2), Page), True)

# Route 3: select_preferences
test_state_3 = make_test_state()
select_preferences(test_state_3, "Phone Case")
assert_equal(test_state_3.selected_application, "Phone Case")

# Route 4: show_results
test_state_4 = make_test_state()
show_results(test_state_4, True, True, False)
assert_equal(test_state_4.priorities, ["High Strength", "Low Density"])
assert_equal(len(test_state_4.recommended_materials) > 0, True)

# Route 5: material_details (both found and not-found cases)
test_state_5 = make_test_state()
material_details(test_state_5, "Titanium Alloy")
assert_equal(test_state_5.selected_material_name, "Titanium Alloy")
assert_equal(test_state_5.status_message, "Viewing details for Titanium Alloy")

material_details(test_state_5, "Fake Material")
assert_equal(
    test_state_5.status_message,
    "Material 'Fake Material' was not found in the database.",
)

# Route 6: compare_materials
test_state_6 = make_test_state()
assert_equal(isinstance(compare_materials(test_state_6), Page), True)

# Route 7: reset_selector
test_state_7 = make_test_state()
test_state_7.selected_application = "Bridge Support"
test_state_7.priorities = ["Low Cost"]
reset_selector(test_state_7)
assert_equal(test_state_7.selected_application, "Bicycle Frame")
assert_equal(test_state_7.priorities, [])
assert_equal(test_state_7.status_message, "Selections have been reset.")


start_server(make_test_state())
