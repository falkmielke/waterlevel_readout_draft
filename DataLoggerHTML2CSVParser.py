#!/usr/bin/env python3

import pathlib as PL
import pandas as PD
from bs4 import BeautifulSoup as BS # I adore this terminology.

#' read a vusitu html file and extract meta info and data
def ReadVuSituHTML(file_path: PL.Path, meta_selection: list = None) -> PD.DataFrame:

    # read file content
    with open(file_path) as fi:
        file_content = BS(fi, "html.parser")
    # print(file_content)
    # data_table = PD.read_html(file_path) # has meta info in table

    ### meta data
    if meta_selection is None:
        meta_selection = ["SerialNumber", "StartTime", "Duration"]

    meta_infos = []
    for mesel in meta_selection:
        info = file_content.find("td", attrs = {"isi-property": mesel}).text
        meta_infos.append(info.split(" = "))

    meta_infos = {k: v for k, v in meta_infos}


    ### data table
    extract_row = lambda row: [td.get_text() for td in row.find_all("td")]

    # header
    header = extract_row(file_content.find("tr", {"class" : "dataHeader"}))

    # data types, used further down
    data_types = file_content.find("tr", {"class" : "dataHeader"}).find_all("td")
    data_types = {
        col: dt for col, dt
        in zip(header, [dt["isi-data-column-header"] for dt in data_types])
    }

    # rowwise data extraction
    data_rows = [
        extract_row(datarow)
        for datarow
        in file_content.find_all("tr", {"class" : "data"})
        ]

    # DataFrame conversion
    data_dict = {
        hd: dat
        for hd, dat in
        list(zip(header, zip(*data_rows)))
        }

    data_table = PD.DataFrame.from_dict(data_dict)

    # data type conversion
    timestamps = [col for col in data_table.columns if data_types[col] == "DateTime"]
    for col in timestamps:
        data_table.loc[:, col ] = PD.to_datetime(data_table.loc[:, col].values)

    # others are float
    data_table.astype({
        col: "float" for col in data_table.columns
        if data_types[col] == "Parameter"
    })
    # print(data_table.dtypes)

    ### done
    return meta_infos, data_table



if __name__ == "__main__":

    # testing
    data_path = PL.Path("test_data")
    test_file = data_path / "VuSitu_Loggen_2025-08-06_12-00-00_Default_Site_BABP042X.html"
    test_output = ReadVuSituHTML(
        test_file,
        meta_selection = ["SerialNumber", "StartTime", "Duration", "FirmwareVersion"]
    )
    print(test_output[0])
    print(test_output[1].head(5))
