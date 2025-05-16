from models.file_reader import FileReader
import matplotlib.pyplot as plt
import numpy as np

print("starting")
filereader = FileReader()

# Extract stars for categorized data
categorized_stars = []
for file_data in filereader.readJsonLines('./data_stages/5_categorized_patch'):
    if 'repository_stars' in file_data:
        star_value = file_data['repository_stars']
        if star_value is not None: # Ensure star value is not None
            categorized_stars.append(star_value)

# Extract stars for raw data
raw_stars = []
for file_data in filereader.readJsonLines('./data_stages/1_raw'):
    if 'repository_stars' in file_data:
        star_value = file_data['repository_stars']
        if star_value is not None: # Ensure star value is not None
            raw_stars.append(star_value)

if not raw_stars:
    print("No star data found in raw dataset ('./data_stages/1_raw'). Cannot compute relative percentages. Exiting.")
    exit()

# Convert to numpy arrays for easier processing
categorized_stars_np = np.array(categorized_stars, dtype=float) # Use float for potential NaNs if any
raw_stars_np = np.array(raw_stars, dtype=float)

# Determine overall min and max stars to define common bin range
# Concatenate only if categorized_stars_np is not empty
if categorized_stars_np.size > 0:
    all_stars = np.concatenate((categorized_stars_np, raw_stars_np))
else:
    all_stars = raw_stars_np

if not all_stars.size > 0:
    print("No star data available to determine bin range after filtering None values. Exiting.")
    exit()

min_star_val = 0  # Start bins from 0 stars
max_star_val = 200000

# Define bin width
bin_width = 5000

# Create bins. Ensure the last bin edge goes up to or beyond max_star_val.
# np.arange's stop is exclusive, so add bin_width to include max_star_val in a bin.
bins = np.arange(min_star_val, max_star_val + bin_width, bin_width)

# If max_star_val is 0 (e.g. all repos have 0 stars), bins might be just [0, 5000] or similar.
# Handle case where bins might be too small or just one bin.
if len(bins) < 2: # Need at least one bin, so at least 2 edges
    if max_star_val == 0: # Special case if all stars are 0
         bins = np.array([0, bin_width]) # Create a single bin [0, 5000)
    else:
        print(f"Warning: Bin generation resulted in insufficient bins (bins: {bins}). Adjusting.")
        # Fallback or specific logic might be needed if this happens unexpectedly.
        # For now, if max_star_val is small, this might be okay.
        if max_star_val < bin_width:
            bins = np.array([0, bin_width])


# Calculate histogram counts for categorized data
categorized_counts, _ = np.histogram(categorized_stars_np, bins=bins)

# Calculate histogram counts for raw data
raw_counts, raw_bin_edges = np.histogram(raw_stars_np, bins=bins) # Use returned bins for consistency

# Calculate relative percentage
relative_percentage = np.zeros_like(raw_counts, dtype=float)

for i in range(len(raw_counts)):
    if raw_counts[i] > 0:
        relative_percentage[i] = (categorized_counts[i] / raw_counts[i]) * 100
    elif categorized_counts[i] > 0 and raw_counts[i] == 0:
        # This means categorized data has items in a bin where raw data has none.
        # This could imply an issue or an interesting finding. Percentage is effectively infinite.
        print(f"Warning: Bin {raw_bin_edges[i]}-{raw_bin_edges[i+1]} has {categorized_counts[i]} categorized items but 0 raw items. Relative percentage set to NaN.")
        relative_percentage[i] = np.nan  # Represent as Not a Number
    # If both categorized_counts[i] and raw_counts[i] are 0, relative_percentage[i] remains 0.0.

# Plotting the relative percentages
plt.figure(figsize=(16, 8))

# Use the actual bin edges returned by histogram for labeling
bin_centers = (raw_bin_edges[:-1] + raw_bin_edges[1:]) / 2

# Filter out NaN values for plotting if any, or let matplotlib handle them (often by not plotting)
valid_indices = ~np.isnan(relative_percentage)

if np.any(valid_indices):
    plt.bar(bin_centers[valid_indices], relative_percentage[valid_indices], width=bin_width * 0.9, align='center', edgecolor='black', label='Relative Percentage')

    # Add text labels for percentages on top of bars
    for i, index in enumerate(np.where(valid_indices)[0]):
        if not np.isnan(relative_percentage[index]):
             plt.text(bin_centers[index], relative_percentage[index] + 0.5, f'{relative_percentage[index]:.1f}%', ha='center', va='bottom', fontsize=8)

    plt.title(f'Relative Percentage of Categorized Repositories to Raw Data by Star Count\n(Bin Width: {bin_width} stars)')
    plt.xlabel('Number of Stars (Star Range Mid-point)')
    plt.ylabel('Relative Percentage (%) [Categorized/Raw * 100]')

    # Create more readable x-tick labels representing ranges
    xtick_labels = [f'{int(raw_bin_edges[i])}-\n{int(raw_bin_edges[i+1]-1)}' for i in range(len(raw_bin_edges)-1)]
    plt.xticks(ticks=bin_centers, labels=xtick_labels, rotation=45, ha="right", fontsize=7)
    
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.show()
else:
    print("No valid data to plot for relative percentages (all NaN or empty).")


if np.any(np.isnan(relative_percentage)):
    print("\nNote: Some bins had 0 raw repositories but >0 categorized repositories, resulting in NaN percentages (not plotted or plotted as gaps).")
    print("Bins with NaN percentages (Star Range: Categorized Count, Raw Count):")
    for i in range(len(relative_percentage)):
        if np.isnan(relative_percentage[i]):
            print(f"  {int(raw_bin_edges[i])}-{int(raw_bin_edges[i+1]-1)}: Cat={categorized_counts[i]}, Raw={raw_counts[i]}")


print("done")