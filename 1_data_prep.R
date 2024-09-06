# Load necessary libraries
library(tidyverse)
library(readxl)

# Define the path to the Excel file
file_path <- "Data Artigao dinamica.xlsx"

# Specify the sheet name or index you want to read
sheet_name <- "Data_individuo"  # Replace with the actual sheet name or use an index like 1

# Read the specific sheet from the Excel file
data <- read_excel(file_path, sheet = sheet_name)

print(head(data))
print(names(data))

colnames(data) <- c(
  "chave_plot_parc_tag_censusno",  # "chave (plot_parc_tag_censusNo)"
  "plot_code",                     # "Plot Code"
  "veget",                         # "Veget"
  "parc",                          # "Parc"
  "tamanho_m2",                    # "Tamanho m^2"
  "tag",                           # "Tag"
  "family",                        # "Family"
  "genus",                         # "genus"
  "species",                       # "Species"
  "census_no",                     # "Census No"
  "census_date",                   # "Census Date"
  "dquad",                         # "Dquad"
  "n_fustes"                       # "N fustes"
)

# Print new column names
print(names(data))

# Convert DAP from mm to cm
data$dquad_cm <- data$dquad / 10

# Convert DAP from cm to meters
data$dquad_m <- data$dquad_cm / 100

# Calculate basal area in square meters (m²)
data$AB_m2 <- (pi * (data$dquad_m)^2) / 4

# Display the data with new columns
print(head(data))

# Filter out rows where 'species' contains the word "indet"
filtered_data <- data %>%
  filter(!str_detect(species, regex("indet", ignore_case = TRUE)))

# Round down 'census_date' and create a new column concatenating it with 'plot_code'
filtered_data <- filtered_data %>%
  mutate(
    census_year = floor(as.numeric(census_date)),  # Assuming 'census_date' is numeric or can be converted to numeric
    plot_census = paste(plot_code, census_year, sep = "_")
  )

# Select specific columns 'plot_census', 'species', 'ab_m2'
selected_data <- filtered_data %>%
  select(plot_census, species, AB_m2)

# Aggregate data: sum 'ab_m2' for each species in each plot_census and count species
aggregated_data <- selected_data %>%
  group_by(plot_census, species) %>%
  summarise(total_ab_m2 = sum(AB_m2, na.rm = TRUE), species_count = n(), .groups = 'drop')

# Pivot the data to have species as rows and plot_census as columns for total_ab_m2
pivoted_ab_data <- aggregated_data %>%
  select(plot_census, species, total_ab_m2) %>%
  pivot_wider(names_from = plot_census, 
              values_from = total_ab_m2, 
              values_fill = list(total_ab_m2 = 0))

# Pivot the data to have species as rows and plot_census as columns for species_count
pivoted_count_data <- aggregated_data %>%
  select(plot_census, species, species_count) %>%
  pivot_wider(names_from = plot_census, 
              values_from = species_count,
              values_fill = list(species_count = 0))

# Display the pivoted data for total_ab_m2
print(pivoted_ab_data)

# Display the pivoted data for species_count
print(pivoted_count_data)

# Calculate relative values for total_ab_m2
pivoted_ab_data_relative <- pivoted_ab_data %>%
  mutate_at(vars(-species), list(~./sum(.)))

# Check if sums to 1
sum(pivoted_ab_data_relative[[2]])

# Calculate relative values for species_count
pivoted_count_data_relative <- pivoted_count_data %>%
  mutate_at(vars(-species), list(~./sum(.)))

# Check if sums to 1
sum(pivoted_count_data_relative[[2]])

# Display the pivoted data for total_ab_m2
print(pivoted_ab_data_relative)

# Display the pivoted data for species_count
print(pivoted_count_data_relative)

# Save the pivoted data with relative values to new CSV files
write_csv(pivoted_ab_data_relative, "aggregated_ab_m2_relative.csv")
write_csv(pivoted_count_data_relative, "aggregated_species_count_relative.csv")
