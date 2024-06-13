# Load necessary libraries
library(tidyverse)
library(readxl)

# Define the path to the Excel file
file_path <- "Data Artigao (1).xlsx"

# Specify the sheet name or index you want to read
sheet_name <- "Data p fuste"  # Replace with the actual sheet name or use an index like 1

# Read the specific sheet from the Excel file
data <- read_excel(file_path, sheet = sheet_name)

print(head(data))
print(names(data))

# Filter out rows where 'species' contains the word "indet"
filtered_data <- data %>%
  filter(!str_detect(Species, regex("indet", ignore_case = TRUE)))

# Select specific columns 'plot_code', 'species', 'ab_m2'
selected_data <- filtered_data %>%
  select(Plot_Code, Species, AB_m2)

# Aggregate data: sum 'ab_m2' for each species in each plot_code and count species
aggregated_data <- selected_data %>%
  group_by(Plot_Code, Species) %>%
  summarise(total_ab_m2 = sum(AB_m2, na.rm = TRUE), species_count = n(), .groups = 'drop')

# Pivot the data to have species as rows and plot_codes as columns for total_ab_m2
pivoted_ab_data <- aggregated_data %>%
  select(Plot_Code, Species, total_ab_m2) %>%
  pivot_wider(names_from = Plot_Code, 
              values_from = total_ab_m2, 
              values_fill = list(total_ab_m2 = 0))

# Pivot the data to have species as rows and plot_codes as columns for species_count
pivoted_count_data <- aggregated_data %>%
  select(Plot_Code, Species, species_count) %>%
  pivot_wider(names_from = Plot_Code, 
              values_from = species_count,
              values_fill = list(species_count = 0))

# Display the pivoted data for total_ab_m2
print(pivoted_ab_data)

# Display the pivoted data for species_count
print(pivoted_count_data)

# Calculate relative values for total_ab_m2
pivoted_ab_data_relative <- pivoted_ab_data %>%
  mutate_at(vars(-Species), list(~./sum(.)))

sum(pivoted_ab_data_relative[[2]])

# Calculate relative values for species_count
pivoted_count_data_relative <- pivoted_count_data %>%
  mutate_at(vars(-Species), list(~./sum(.)))

sum(pivoted_count_data_relative[[2]])

# Display the pivoted data for total_ab_m2
print(pivoted_ab_data_relative)

# Display the pivoted data for species_count
print(pivoted_count_data_relative)

# Save the pivoted data with relative values to new CSV files
write_csv(pivoted_ab_data_relative, "aggregated_ab_m2_relative.csv")
write_csv(pivoted_count_data_relative, "aggregated_species_count_relative.csv")
