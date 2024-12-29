pacman::p_load(tidyverse, ggplot2, here, knitr, kableExtra)

df <- read_csv("./data/raw_data.csv", col_types = "cccnn") |>
  mutate(date = ymd(date)) |>
  arrange(date)
cat("New data retrieved and loaded \n")

# Format country name
country_names <- c("United States" = "U.S.")

df <- df |>
  mutate(country = case_when(
    country %in% names(country_names) ~ country_names[country],
    .default = country
  ))

# The latest date and date range
date_latest <- last(df$date)
date_first <- first(df$date)
date_range <- paste0(
  "From ",
  date_first,
  " to ",
  date_latest - 1
)

# Mean across dates
df_summary <- df |>
  mutate(latest = (date == date_latest)) |>
  group_by(country, city, latest) |>
  summarise(
    activeUsers = sum(activeUsers),
    newUsers = sum(newUsers),
    .groups = "drop"
  )

df_past <- df_summary |>
  filter(!latest) |>
  select(-latest) |>
  arrange(desc(activeUsers)) |>
  slice(1:10)

df_today <- df_summary |>
  filter(latest) |>
  select(-latest) |>
  arrange(desc(activeUsers)) |>
  slice(1:10)

# Add ghost rows to df_today to make the lenghts the same
df_today <- df_today |>
  add_row(country = rep(" '", nrow(df_past) - nrow(df_today))) |>
  mutate(across(everything(), ~ replace(.x, is.na(.x), " ' ")))

# HTML
cat("Saving data... \n")

df_past_table <- kable(df_past |> slice(1:10),
  valign = "t",
  align = "c",
  caption = date_range,
  format = "html"
) |>
  kable_styling(
    full_width = TRUE,
    fixed_thead = TRUE
  )

save_kable(df_past_table,
  self_contained = FALSE,
  format = "html",
  file = "./df_past_html.txt"
)

df_today_table <- kable(df_today,
  valign = "t",
  align = "c",
  caption = paste0("On ", date_latest),
  format = "html"
) |>
  kable_styling(
    full_width = TRUE,
    fixed_thead = TRUE
  )

save_kable(df_today_table,
  self_contained = FALSE,
  format = "html",
  file = "./df_today_html.txt"
)

df_summary <- kables(list(df_past_table, df_today_table),
  caption = paste0("Summary: ", Sys.Date()),
  format = "html"
)

save_kable(df_summary,
  self_contained = FALSE,
  format = "html",
  file = "./df_html.txt"
)

cat(paste0("Html table succesfully updated! ", Sys.Date()))
