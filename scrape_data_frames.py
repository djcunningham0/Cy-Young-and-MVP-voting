from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from datetime import datetime
import os


def get_soup(url, headers=None, verbose=True):
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        if verbose:
            print("Failed to connect to {} with error code: {}".format(url, result.status_code))
        return None
    else:
        soup = bs(result.content, 'html5lib')
        return soup


def scrape_cy(year=datetime.today().year, league="", directory="./data/", verbose=True):
    if league.upper() == "AL":
        url = "https://bbwaa.com/" + str(year)[-2:] + "-al-cy/"
    elif league.upper() == "NL":
        url = "https://bbwaa.com/" + str(year)[-2:] + "-nl-cy/"
    else:
        print("Must specify league as AL or NL.")
        return None

    # get the HTML
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    soup = get_soup(url, headers, verbose=verbose)

    # get the two tables -- first is summary, second is individual voter lists
    tables = soup.find_all('table')

    summary = table_to_dataframe(tables[0])
    detail = table_to_dataframe(tables[1])

    # create directory if it doesn't exist and make sure it ends in "/"
    directory = set_directory(directory)

    file_prefix = directory + str(year) + "_" + league.upper() + "_CyYoung_"
    summary.to_csv(file_prefix + "summary.csv", index=False)
    detail.to_csv(file_prefix + "detail.csv", index=False)


def scrape_mvp(year=datetime.today().year, league="", verbose=True):
    if league.upper() == "AL":
        summary_url = "https://bbwaa.com/" + str(year)[-2:] + "-al-mvp/"
        detail_url = "https://bbwaa.com/" + str(year)[-2:] + "-al-mvp-ballots/"
    elif league.upper() == "NL":
        summary_url = "https://bbwaa.com/" + str(year)[-2:] + "-nl-mvp/"
        detail_url = "https://bbwaa.com/" + str(year)[-2:] + "-nl-mvp-ballots/"
    else:
        print("Must specify league as AL or NL.")
        return None

    # get the HTML
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    summary_soup = get_soup(summary_url, headers, verbose=verbose)
    detail_soup = get_soup(detail_url, headers, verbose=verbose)

    summary_table = summary_soup.find('table')
    detail_table = detail_soup.find('table')

    summary = table_to_dataframe(summary_table)
    detail = table_to_dataframe(detail_table)

    file_prefix = "./data/" + str(year) + "_" + league.upper() + "_MVP_"
    summary.to_csv(file_prefix + "summary.csv", index=False)
    detail.to_csv(file_prefix + "detail.csv", index=False)


def table_to_dataframe(table):
    df = pd.DataFrame()

    # get the column names
    columns = table.find_all('th')
    col_classes = []
    col_names = []
    for col in columns:
        col_classes.append(col.get('class')[0])
        col_names.append(col.text.strip())

    # get the data for each column and add to dataframe
    # data = []
    for i, cls in enumerate(col_classes):
        # data.append([])
        col_data = []
        for val in table.find_all('td', class_=cls):
            # data[i].append(val.text)
            col_data.append(val.text)

        df[col_names[i]] = col_data

    return df


def set_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    if directory[-1] != "/":
        directory += "/"

    return directory


def scrape_al_cy(year=datetime.today().year, verbose=True):
    scrape_cy(year=year, league="AL", verbose=verbose)


def scrape_nl_cy(year=datetime.today().year, verbose=True):
    scrape_cy(year=year, league="NL", verbose=verbose)


def scrape_al_mvp(year=datetime.today().year, verbose=True):
    scrape_mvp(year=year, league="AL", verbose=verbose)


def scrape_nl_mvp(year=datetime.today().year, verbose=True):
    scrape_mvp(year=year, league="NL", verbose=verbose)


for year in range(2012, 2019):
    scrape_al_cy(year=year)
    scrape_nl_cy(year=year)
    scrape_al_mvp(year=year)
    scrape_nl_mvp(year=year)
