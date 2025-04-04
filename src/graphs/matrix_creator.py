import plotly.graph_objects as go

bug_types = [
    "Buffer Overflow",
    "Memory leak",
    "Null pointer", # Corrected typo from "null pointer"
    "Race condition", # Corrected typo from "race condition"
]

patch_types = [
    "Null check",   # Corrected typo from "null check"
    "Try-except", # Corrected typo from "try-except"
    "Library change",
]

# Ensure dictionary keys match the lowercase versions of the list items
bug_to_patch_probabilities = {
    "buffer overflow": {
        "null check": 0.7,
        "try-except": 0.2,
        "library change": 0.1,
    },
    "memory leak": {
        "null check": 0.3,
        "try-except": 0.5,
        "library change": 0.2,
    },
    "null pointer": { # Key matches lowercase "Null pointer"
        "null check": 0.6,
        "try-except": 0.3,
        "library change": 0.1,
    },
    "race condition": { # Key matches lowercase "Race condition"
        "null check": 0.4,
        "try-except": 0.4,
        "library change": 0.2,
    },
}

def create_beautiful_table(bug_types, patch_types, bug_to_patch_probabilities):
    """
    Creates a visually appealing Plotly table from bug types, patch types,
    and their corresponding probabilities.

    Args:
        bug_types (list): A list of bug type strings (e.g., "Buffer Overflow").
        patch_types (list): A list of patch type strings (e.g., "Null check").
        bug_to_patch_probabilities (dict): A nested dictionary where
            outer keys are lowercase bug types, inner keys are lowercase
            patch types, and values are probabilities.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure containing the table.
    """

    # Prepare header values
    header_values = ['<b>Bug Type</b>'] + [f'<b>{pt}</b>' for pt in patch_types]

    # Prepare cell values (column-wise)
    # First column is the bug types
    cell_values = [bug_types]

    # Subsequent columns are the probabilities for each patch type
    for patch_type in patch_types:
        patch_key = patch_type.lower() # Use lowercase for dict lookup
        column_probs = []
        for bug_type in bug_types:
            bug_key = bug_type.lower() # Use lowercase for dict lookup
            # Get probability, default to 'N/A' if not found
            probability = bug_to_patch_probabilities.get(bug_key, {}).get(patch_key, 'N/A')
            # Format as percentage if it's a number
            if isinstance(probability, (int, float)):
                 column_probs.append(f"{probability:.1%}") # Format as percentage
            else:
                 column_probs.append(probability) # Keep 'N/A' or other strings as is

        cell_values.append(column_probs)

    # Create the table figure
    fig = go.Figure(data=[go.Table(
        header=dict(values=header_values,
                    fill_color='paleturquoise',
                    align='center',
                    font=dict(color='black', size=12)),
        cells=dict(values=cell_values,
                   fill_color='lavender',
                   align=['left', 'center'], # Align first column left, others center
                   font=dict(color='black', size=11),
                   height=30) # Increase cell height for better spacing
    )])

    # Add a title and adjust layout for aesthetics
    fig.update_layout(
        title_text='Bug Type vs. Patch Type Probabilities',
        title_x=0.5, # Center title
        margin=dict(l=20, r=20, t=50, b=20) # Adjust margins
    )

    return fig

# --- Example Usage ---
if __name__ == "__main__":
    # Create the table
    beautiful_table_figure = create_beautiful_table(bug_types, patch_types, bug_to_patch_probabilities)

    # Show the table
    beautiful_table_figure.write_image("bug_patch_table.png")

    # Optional: Save the table as an HTML file
    # beautiful_table_figure.write_html("bug_patch_table.html")