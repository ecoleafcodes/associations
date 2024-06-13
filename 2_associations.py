import pandas as pd
import numpy as np
import itertools

from joblib import Parallel, delayed
import multiprocessing

from tqdm import tqdm
import matplotlib.pyplot as plt


def compute_associations(csv_path):
    # Read the CSV file
    data = pd.read_csv(csv_path)

    # Get the 'species' column
    species_column = data['Species']

    # Create a mapper for species to index
    species_mapper = {species: index for index, species in enumerate(species_column.unique())}
    inverse_species_mapper = {index: species for species, index in species_mapper.items()}

    # Get the vector of each species and build a NumPy matrix
    species_vectors = []
    for species, group in data.groupby('Species'):
        species_vector = group.drop(columns=['Species']).values.flatten()
        species_vectors.append(species_vector)

    # Convert the list of species vectors to a NumPy matrix
    species_matrix = np.vstack(species_vectors)

    association_matrix = np.dot(species_matrix, species_matrix.T)

    # Create a list of all 2x2 combinations of indexes
    index_combinations = list(itertools.combinations(range(len(species_mapper)), 2))

    # Iterate over each combination, too slow, let's parallelize
    # for index_a, index_b in tqdm(index_combinations):
    #     species_a = inverse_species_mapper[index_a]
    #     species_b = inverse_species_mapper[index_b]
    #     association = association_matrix[index_a, index_b]
    #     results_df = results_df.append({'species_a': species_a, 'species_b': species_b, 'association': association}, ignore_index=True)


    num_cores = multiprocessing.cpu_count()

    # Define a function to process each combination
    def process_combination(index_combination, inverse_species_mapper, association_matrix):
        index_a, index_b = index_combination
        species_a = inverse_species_mapper[index_a]
        species_b = inverse_species_mapper[index_b]
        association = association_matrix[index_a, index_b]
        return {'species_a': species_a, 'species_b': species_b, 'association': association}

    # Parallelize the iteration
    results_list = Parallel(n_jobs=num_cores)(delayed(process_combination)(index_combination, 
                                                                           inverse_species_mapper, 
                                                                           association_matrix) for \
                                                                            index_combination in tqdm(index_combinations))

    # Convert the results list to a DataFrame
    results_df = pd.DataFrame(results_list)

    return results_df


# Path to the CSV file
associations_ab = compute_associations("aggregated_ab_m2_relative.csv")
associations_count = compute_associations("aggregated_species_count_relative.csv")

associations_ab.sort_values(by='association', ascending=False, inplace=True)
associations_count.sort_values(by='association', ascending=False, inplace=True)

# Save the results to CSV files
associations_ab.to_csv('species_associations_ab.csv', index=False)
associations_count.to_csv('species_associations_count.csv', index=False)


# plt.hist(associations_ab_sorted['association'], bins=50, color='skyblue', edgecolor='black')
# plt.show()

# associations_ab_positive = associations_ab_sorted[associations_ab_sorted['association'] > 0]
# plt.hist(associations_ab_positive['association'], bins=500, color='skyblue', edgecolor='black')
# plt.show()
