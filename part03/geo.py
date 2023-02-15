# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
# muzete pridat vlastni knihovny


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovani

    :param df: pandas.DataFrame
    :return: geopandas.GeoDataFrame
    """

    df.dropna(subset=['d'], inplace=True)
    df.dropna(subset=['e'], inplace=True)

    return geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.d, df.e), crs="EPSG:5514")


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji

    :param gdf: geopandas.GeoDataFrame
    :param fig_location: cesta, kam se ma graf ulozit
    :param show_figure: zda se ma graf zobrazit
    """

    data = gdf[gdf["region"] == "JHM"].copy()

    data["p2a"] = pd.to_datetime(data["p2a"]).astype("datetime64")
    data["year"] = data[data["p2a"].dt.year >= 2018]["p2a"].dt.year.copy()
    data = data[data["year"] >= 2018].astype({"year": "int32"})

    data = data.to_crs(epsg=3857)

    years = [2018, 2019, 2020, 2021]

    data = data[data["p11"] >= 3].copy()

    fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    # plot those subplots for each year
    for year, ax in zip(years, axes.flatten()):
        data.loc[data["year"] == year].plot(ax=ax, markersize=1, color="red")
        ax.set_title(f"Kraj JHM {year}")
        ctx.add_basemap(ax=ax, crs=data.crs.to_string(),
                        source=ctx.providers.Stamen.TonerLite)
        ax.set_axis_off()
        plt.tight_layout()

    if fig_location:
        plt.savefig(fig_location)
    if show_figure:
        plt.show()


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru

    :param gdf: geopandas.GeoDataFrame
    :param fig_location: cesta, kam se ma graf ulozit
    :param show_figure: zda se ma graf zobrazit
    """

    data = gdf[gdf["region"] == "JHM"].copy()
    data = data.loc[data["p36"].isin([1, 2, 3])]

    cords = np.array([data.geometry.x, data.geometry.y]).T

    data["cluster"] = sklearn.cluster.KMeans(n_clusters=25).fit(cords).labels_

    data = data.to_crs(epsg=3857)
    data = data.dissolve(by="cluster", aggfunc={"p1": "count"})

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    data.plot(ax=ax, column="p1", markersize=2, alpha=0.5, legend=True, legend_kwds={
              'label': "Počet nehod", 'orientation': "horizontal", "pad": 0.01})
    ctx.add_basemap(ax, crs=data.crs.to_string(),
                    source=ctx.providers.Stamen.TonerLite)
    ax.set_axis_off()
    plt.tight_layout()

    if fig_location:
        plt.savefig(fig_location)
    if show_figure:
        plt.show()


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
