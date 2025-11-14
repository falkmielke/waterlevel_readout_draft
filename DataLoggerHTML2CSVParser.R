#!/usr/bin/Rscript

# # Load the packages
# library("rvest")
# library("xml2")
# library("dplyr")
# library("janitor") # to cleanup the data

# this is loading a test file
test_file <- here::here(
  "test_data",
  "VuSitu_Loggen_2025-08-06_12-00-00_Default_Site_BABP042X.html"
  )


#' read a vusitu html file and extract meta info and data
#'
#' @param file_path a path to the file which shall be read
#' @param meta_selection character array of meta data tags to read
#' @return a list with the elements "meta" (list) and "data" (tibble)
#'
read_vusitu_html <- function(file_path, meta_selection = NULL) {

  # does file exist?
  if (isFALSE(file.exists(file_path))) stop("File not found.")

  # libraries
  stopifnot(
    "rvest" = require("rvest"),
    "xml2" = require("xml2"),
    "dplyr" = require("dplyr"),
    "janitor" = require("janitor")
  )

  # read in the raw html
  # https://www.geeksforgeeks.org/web-scraping/scrape-an-html-table-using-rvest-in-r
  logger_readout_raw <- rvest::read_html(file_path)

  # get meta node content
  meta_nodes <- logger_readout_raw %>%
    rvest::html_elements(".sectionMember") %>%
    rvest::html_nodes("td")

  if (is.null(meta_selection)) {
    meta_selection <- c("SerialNumber", "StartTime", "Duration")
  }

  select_node <- function(isi_properties) meta_nodes %>%
    rvest::html_attr("isi-property") %in% isi_properties
  meta_info <- meta_nodes[select_node(meta_selection)] %>%
    rvest::html_text()

  # format into named list
  meta_info <- sapply(meta_info, FUN = function(info) strsplit(info, " = "))
  names(meta_info) <- sapply(meta_info, `[[`, 1)
  meta_info <- sapply(meta_info, `[[`, 2)

  # # in principle, this can get only data nodes,
  # but I was unsuccesful to use them further
  # logger_readout_raw %>% html_nodes(".data")

  # find the raw table
  table_raw <- logger_readout_raw %>% rvest::html_elements("table")


  # find rows of the correct classes ("data" and "dataHeader")
  data_rows <- unlist(
      lapply(
        table_raw %>% rvest::html_elements("tr"),
        FUN = function(tr) tr %>% rvest::html_attr("class")
      )
    ) %>% startsWith("data")
  data_rows[is.na(data_rows)] <- FALSE # NANs are not data rows

  # this assumes that only one table is present
  table_data <- table_raw %>%
    rvest::html_table() %>%
    .[[1]] %>%
    .[data_rows,] %>%
    dplyr::filter(dplyr::if_all(dplyr::everything(), ~ !is.na(.x))) %>%
    janitor::row_to_names(row = 1) # first row is dataHeader

  # data type cleanup
  table_data <- table_data %>%
    dplyr::mutate_at(
      dplyr::vars(dplyr::starts_with("Datum")),
      function(ts) as.POSIXct(ts, format = "%Y-%m-%d %H:%M:%OS")
      ) %>%
    mutate_at(
      dplyr::vars(dplyr::starts_with(c("Temperatuur", "Diepte", "Druk"))),
      ~as.numeric(.) # ~readr::parse_number(.)
      )

  return(list(
    "meta" = meta_info,
    "data" = table_data
  ))
} # /read_vusitu_html

# options(digits = 12, digits.secs = 4)
test_output <- read_vusitu_html(
  file_path = test_file,
  meta_selection = c("SerialNumber", "StartTime", "Duration", "FirmwareVersion")
)
test_output["meta"] %>% knitr::kable(col.names = NULL, format = "pandoc")
test_output["data"] %>% knitr::kable(digits = Inf)
# test_output %>% pull("Datum Tijd") %>% format("%Y%m%d %H:%M:%OS6")
