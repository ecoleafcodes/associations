import pandas as pd
import numpy as np
import itertools

from tqdm import tqdm
import matplotlib.pyplot as plt


# Define the path to the Excel file
file_path = "Data Artigao dinamica.xlsx"

# Specify the sheet name you want to read
sheet_name = "Data_individuo"

# Read the specific sheet from the Excel file into a DataFrame named 'data_census'
data_census = pd.read_excel(file_path, sheet_name=sheet_name)

# Ensure 'census_date' is numeric, round down to the nearest integer
# Assuming 'census_date' is a numeric or datetime column
data_census['census_year'] = np.floor(pd.to_numeric(data_census['Census Date'], errors='coerce'))

# Create the 'plot_census' column by concatenating 'plot_code' and 'census_year'
data_census['plot_census'] = data_census['Plot Code'].astype(str) + "_" + data_census['census_year'].astype(int).astype(str)

df_plot_census = data_census[['plot_census', 'Plot Code']].drop_duplicates().reset_index(drop=True).rename(columns={"Plot Code": "plot_code"})

df_plot_codes = df_plot_census[['plot_code']].drop_duplicates()
plot_codes = list(df_plot_codes['plot_code'])

plot_codes_cache = {}
for plot_code in plot_codes:
    # Filter df_plot_census to get the plot_census rows for the current plot_code
    filtered_df = df_plot_census[df_plot_census['plot_code'] == plot_code]
    plot_codes_cache[plot_code] = filtered_df['plot_census'].tolist()


def compute_associations(csv_path):

    # Read the CSV file
    data = pd.read_csv(csv_path)
    data.head()

    combinations = list(itertools.combinations(data['species'], 2))
    # len(combinations)

    associations_result = {}
    
    for comb in tqdm(combinations):

        associations_by_plot = []

        df_sps = data[(data['species'].isin(comb))]

        for plot_code in plot_codes:

            # Get the list of plot_census values from the filtered_df
            plot_census_values = plot_codes_cache[plot_code]
            
            # Select columns from df_sps that are in plot_census_values
            columns_to_keep = ['species'] + plot_census_values
            filtered_sps = df_sps.loc[:, columns_to_keep]

            n_census = len(plot_census_values)
                
            # Convert the 'filtered_sps' DataFrame (excluding the 'species' column) to a NumPy array
            sps_array = filtered_sps.drop(columns='species').to_numpy()

            # Extract the two rows (each row is a species)
            row1 = sps_array[0]
            row2 = sps_array[1]

            associations_by_plot += np.dot(row1, row2) / n_census,

        association = sum(np.array(associations_by_plot))
        associations_result[comb] = association

    associations_result = pd.DataFrame(
        [(a, b, assoc) for (a, b), assoc in associations_result.items()],
        columns=['species_a', 'species_b', 'association']
        )

    return associations_result


# Path to the CSV file
associations_ab = compute_associations("aggregated_ab_m2_relative.csv")
associations_count = compute_associations("aggregated_species_count_relative.csv")

associations_ab.sort_values(by='association', ascending=False, inplace=True)
associations_count.sort_values(by='association', ascending=False, inplace=True)

# Save the results to CSV files
associations_ab.to_csv('species_associations_ba.csv', index=False)
associations_count.to_csv('species_associations_count.csv', index=False)


# plt.hist(associations_ab['association'], bins=50, color='skyblue', edgecolor='black')
# plt.show()

# associations_ab_positive = associations_ab[associations_ab['association'] > 0]
# plt.hist(associations_ab_positive['association'], bins=500, color='skyblue', edgecolor='black')
# plt.show()
