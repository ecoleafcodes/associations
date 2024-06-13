# Load necessary libraries
library(dplyr)
library(readxl)
library(ggplot2)
library(viridis)
library(sf)



# Function to process data and generate plot and CSV
process_data <- function(file_path, plot_file, csv_file) {
    
  # Read data from CSV file
  data <- read.csv(file_path)
  
  # Read metadata from Excel file
  file_path_meta <- "Data Artigao (1).xlsx"
  metadata <- read_excel(file_path_meta, sheet = "Metadata")
  
  # Merge data with metadata
  merged_data <- data %>%
    left_join(metadata, by = c("site" = "Plot Code")) %>%
    select(site, average_association, `Latitude Decimal`, `Longitude Decimal`) %>%
    rename(lon = `Longitude Decimal`, lat = `Latitude Decimal`)
  
  merged_data_sf <- st_as_sf(merged_data, coords = c("lon", "lat"), crs = 4326)
  
  # Plot
  plot <- ggplot() +
    geom_sf(data = merged_data_sf, aes(color = average_association), size = 4, alpha = 0.8) +
    scale_color_viridis_c(option = "magma", begin = 0.1, end = 0.9) +
    labs(title = "",
         x = "Longitude",
         y = "Latitude",
         color = "Association") +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5),
      legend.title = element_text(size = 12),
      legend.text = element_text(size = 10)
    )
  
  # Save plot
  ggsave(plot_file, plot, width = 7, height = 7, dpi = 200)
  
  # Save merged data to CSV
  write.csv(merged_data, csv_file, row.names = FALSE)
  
  # Return the plot and CSV filenames
  return(list(plot_file = plot_file, csv_file = csv_file))
}

process_data("average_species_associations_ab.csv",
             "average_association_per_site_ab.jpeg", 
             "average_association_per_site_ab.csv")


process_data("average_species_associations_count.csv",
             "average_association_per_site_count.jpeg", 
             "average_association_per_site_count.csv")