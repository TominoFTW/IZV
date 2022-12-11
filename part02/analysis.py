#!/usr/bin/env python3.9
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import zipfile

# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

# Ukol 1: nacteni dat ze ZIP souboru


def load_data(filename: str) -> pd.DataFrame:
    """
    Loads data from a zip file and returns a pandas DataFrame.

    :param filename: name of the zip file

    :return: pandas DataFrame
    """
    # tyto konstanty nemente, pomuzou vam pri nacitani
    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    # def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }
    df = []
    with zipfile.ZipFile(filename, 'r') as zip:
        for year_file in zip.namelist():
            with zipfile.ZipFile(zipfile.ZipFile.open(zip, year_file)) as zip2:
                for file in zip2.namelist():
                    if file != "CHODCI.csv":
                        tmp = pd.read_csv(zip2.open(
                            file), sep=";", header=None, names=headers, encoding="cp1250", low_memory=False)
                        tmp["region"] = {v: k for k, v in regions.items()}.get(
                            file.removesuffix(".csv"))
                        df.append(tmp)

    return pd.concat(df, ignore_index=True)

# Ukol 2: zpracovani dat


def parse_data(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """
    Parses the data and returns a pandas DataFrame.

    :param df: pandas DataFrame
    :param verbose: whether to print additional information

    :return: pandas DataFrame
    """
    new_df = df.copy()
    new_df = new_df.drop_duplicates(subset="p1")

    new_df["date"] = pd.to_datetime(new_df["p2a"]).astype("datetime64")

    category_cols = ["k", "p", "q", "t", "l"]
    nums_cols = ["p1", "p36", "p37", "p2a", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
                 "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
                 "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
                 "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "n", "o", "r", "s", "p5a"]

    new_df[category_cols] = new_df[category_cols].astype("category")
    new_df[nums_cols] = new_df[nums_cols].apply(pd.to_numeric, errors="coerce")

    if verbose:
        print(f"orig_size={df.memory_usage(deep=True).sum() / 10**6:.1f} MB")
        print(
            f"new_size={new_df.memory_usage(deep=True).sum() / 10**6:.1f} MB")
    return new_df

# Ukol 3: počty nehod v jednotlivých regionech podle viditelnosti


def plot_visibility(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    """
    Plots the number of accidents from 4 region with dependence on visibility.

    :param df: pandas DataFrame
    :param fig_location: location to save the figure
    :param show_figure: whether to show the figure
    """
    visibility = {
        1: "Viditelnost ve dne - nezhoršená",
        2: "Viditelnost ve dne - zhoršená",
        3: "Viditelnost ve dne - zhoršená",
        4: "Viditelnost v noci - nezhoršená",
        5: "Viditelnost v noci - zhoršená",
        6: "Viditelnost v noci - nezhoršená",
        7: "Viditelnost v noci - zhoršená",
    }
    selected_regions = ["OLK", "ZLK", "VYS", "PAK"]

    df = df[df["region"].isin(selected_regions)].copy()
    df["p19_visibility"] = df["p19"].map(visibility)

    grouped = df.groupby(["region", "p19_visibility"]).agg(
        {"p1": "nunique"}).reset_index()

    sns.set_context("paper", font_scale=1.5)
    sns.set_style("whitegrid")

    graph = sns.catplot(x="region", y="p1", col="p19_visibility", data=grouped, kind="bar", col_wrap=2, sharey=False, col_order=[
                        "Viditelnost ve dne - nezhoršená",  "Viditelnost ve dne - zhoršená",  "Viditelnost v noci - nezhoršená", "Viditelnost v noci - zhoršená"])

    graph.set_titles("{col_name}")
    graph.set_xlabels("Kraje")
    graph.set_ylabels("Počet nehod")
    graph.fig.suptitle("Počet nehod podle viditelnosti a podle dne či noci")
    graph.fig.subplots_adjust(top=0.9)

    if fig_location:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()

# Ukol4: druh srážky jedoucích vozidel


def plot_direction(df: pd.DataFrame, fig_location: str = None,
                   show_figure: bool = False):
    """
    Plots the number of accidents from 4 region with dependence on direction.

    :param df: pandas DataFrame
    :param fig_location: location to save the figure
    :param show_figure: whether to show the figure
    """
    direction = {
        1: "Čelní",
        2: "Boční",
        3: "Boční",
        4: "Zezadu",
    }
    selected_regions = ["OLK", "ZLK", "VYS", "PAK"]

    df = df[df["p7"] != 0]
    df = df[df["region"].isin(selected_regions)]
    df["p7"] = df["p7"].map(direction)
    df["month"] = df["date"].dt.month

    grouped = df.groupby(["region", "p7", "month"]).agg(
        {"p1": "nunique"}).reset_index()

    sns.set_context("paper", font_scale=1.5)
    sns.set_style("whitegrid")

    graph = sns.catplot(x="month", y="p1", hue="p7", col="region",
                        data=grouped, kind="bar", col_wrap=2, sharey=False)

    graph.set_titles("Kraj: {col_name}")
    graph.fig.subplots_adjust(top=0.9, left=0.1, right=0.85)
    graph.fig.subplots_adjust(hspace=0.2, wspace=0.2)
    graph._legend.set_title("Druh srážky")

    for subplot in graph.axes.flatten():
        subplot.tick_params(labelbottom=True)
        subplot.set_xlabel("Měsíc")
        subplot.set_ylabel("Počet nehod")

    if fig_location:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()

# Ukol 5: Následky v čase


def plot_consequences(df: pd.DataFrame, fig_location: str = None,
                      show_figure: bool = False):
    """
    Plots the number of accidents from 4 region with dependence on consequences.

    :param df: pandas
    :param fig_location: location to save the figure
    :param show_figure: whether to show the figure
    """
    pass


if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni
    # funkce.
    df = load_data("data/data.zip")
    df2 = parse_data(df, True)

    plot_visibility(df2, "01_visibility.png")
    plot_direction(df2, "02_direction.png")
    plot_consequences(df2, "03_consequences.png")


# Poznamka:
# pro to, abyste se vyhnuli castemu nacitani muzete vyuzit napr
# VS Code a oznaceni jako bunky (radek #%%% )
# Pak muzete data jednou nacist a dale ladit jednotlive funkce
# Pripadne si muzete vysledny dataframe ulozit nekam na disk (pro ladici
# ucely) a nacitat jej naparsovany z disku
