import itertools
import numpy as np
import pandas as pd


def compute_site_average_association(association_data, sp_sites_data):
    
    # Create a dictionary to quickly lookup association values
    association_dict = {}
    for _, row in association_data.iterrows():
        association_dict[(row['species_a'], row['species_b'])] = row['association']
        association_dict[(row['species_b'], row['species_a'])] = row['association']

    # Initialize a list to store average associations for each column
    average_associations = []

    # Iterate over the columns (excluding the first column which is 'Species')
    for column in sp_sites_data.columns[1:]:
        # Filter species with value > 0
        filtered_species = sp_sites_data[sp_sites_data[column] > 0]['Species']
        
        # Generate all combinations of species pairs
        species_pairs = itertools.combinations(filtered_species, 2)
        
        # Get association values for each pair and calculate the average
        associations = [
            association_dict.get((species_a, species_b), np.nan) 
            for species_a, species_b in species_pairs
        ]
        
        # Filter out NaN values and calculate the average
        valid_associations = [assoc for assoc in associations if not np.isnan(assoc)]
        if valid_associations:
            average_associations.append(np.mean(valid_associations))
        else:
            average_associations.append(np.nan)

    # Create a DataFrame with the results
    results_df = pd.DataFrame({
        'site': sp_sites_data.columns[1:], 
        'average_association': average_associations
    })

    return results_df


# Read the CSV files
file_path_associations = "species_associations_ab.csv"
association_data = pd.read_csv(file_path_associations)

file_path_sp_sites = "aggregated_ab_m2_relative.csv"
sp_sites_data = pd.read_csv(file_path_sp_sites)

ab_results_df = compute_site_average_association(association_data, sp_sites_data)

# Save the results to a CSV file
ab_results_df.to_csv('average_species_associations_ab.csv', index=False)


# Read the CSV files
file_path_associations = "species_associations_count.csv"
association_data = pd.read_csv(file_path_associations)

file_path_sp_sites = "aggregated_species_count_relative.csv"
sp_sites_data = pd.read_csv(file_path_sp_sites)

count_results_df = compute_site_average_association(association_data, sp_sites_data)

# Save the results to a CSV file
count_results_df.to_csv('average_species_associations_count.csv', index=False)