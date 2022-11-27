#!/usr/bin/env python3
"""
IZV cast1 projektu
Autor: xbehal02

Detailni zadani projektu je v samostatnem projektu e-learningu.
Nezapomente na to, ze python soubory maji dane formatovani.

Muzete pouzit libovolnou vestavenou knihovnu a knihovny predstavene na prednasce
"""


from bs4 import BeautifulSoup
import requests
import numpy as np
import matplotlib.pyplot as plt
from typing import List


def integrate(x: np.array, y: np.array) -> float:
    ret = np.sum(np.multiply(
        (np.subtract(x[1:], x[:-1])), (np.add(y[:-1], y[1:]))/2))
    return ret


def generate_graph(a: List[float], show_figure: bool = False, save_path: str | None = None):
    x = np.linspace(-3, 3, 1000)
    a = np.reshape(a, (len(a), 1))
    y = a * np.power(x, 2)

    fig = plt.figure(figsize=(7, 4))
    ax = fig.add_subplot()

    ax.spines['right'].set_position(("outward", 0))

    ax.plot(x, y[0], label="$y_{1.0}(x)$", color="blue")
    ax.plot(x, y[1], label="$y_{2.0}(x)$", color="orange")
    ax.plot(x, y[2], label="$y_{-2.0}(x)$", color="green")

    plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    ax.set_xlim(-3, 4.2)
    plt.xlabel("x")
    ax.set_yticks([-20, -15, -10, -5, 0, 5, 10, 15, 20])
    plt.ylim(-20, 20)
    plt.ylabel("$f_a(x)$")

    plt.annotate(R"$\int f_{1.0}(x)dx$", xy=(3, 8), xytext=(3, 8))
    plt.annotate(R"$\int f_{2.0}(x)dx$", xy=(3, 17), xytext=(3, 17))
    plt.annotate(R"$\int f_{-2.0}(x)dx$", xy=(3, 19), xytext=(3, -19))

    plt.fill_between(x, y[0], where=y[0] > 0, color="blue", alpha=0.1)
    plt.fill_between(x, y[1], where=y[1] > 0, color="orange", alpha=0.1)
    plt.fill_between(x, y[2], where=y[2] < 0, color="green", alpha=0.1)

    if show_figure:
        plt.show()
    if save_path:
        plt.savefig(save_path)
    plt.close()


def generate_sinus(show_figure: bool = False, save_path: str | None = None):
    t = np.linspace(0, 100, 10000)

    y1 = 0.5 * np.sin(t * (np.pi / 50))
    y2 = 0.25 * np.sin(np.pi * t)
    y3 = np.add(y1, y2)

    fig = plt.figure()

    ax = fig.add_subplot(3, 1, 1)
    bx = fig.add_subplot(3, 1, 2)
    cx = fig.add_subplot(3, 1, 3)

    fig.set_figheight(10)
    fig.set_figwidth(7.5)

    ax.plot(t, y1, color="blue")
    bx.plot(t, y2, color="blue")
    cx.plot(t, y3, color="green")
    cx.plot(t, np.ma.masked_greater(y3, y1), color="red")

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.8, 0.8)
    ax.set_yticks([-0.8, -0.4, 0, 0.4, 0.8])
    ax.set_xlabel("t")
    ax.set_ylabel("$f_1(x)$")

    bx.set_xlim(0, 100)
    bx.set_ylim(-0.8, 0.8)
    bx.set_yticks([-0.8, -0.4, 0, 0.4, 0.8])
    bx.set_xlabel("t")
    bx.set_ylabel("$f_2(x)$")

    cx.set_xlim(0, 100)
    cx.set_ylim(-0.8, 0.8)
    cx.set_yticks([-0.8, -0.4, 0, 0.4, 0.8])
    cx.set_xlabel("t")
    cx.set_ylabel("$f_1(x) + f_2(x)$")

    if show_figure:
        plt.show()
    if save_path:
        plt.savefig(save_path)


def download_data(url="https://ehw.fit.vutbr.cz/izv/temp.html"):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')
    data = []

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        colsChecked = []
        for i in range(len(cols)):
            if len(cols[i]) < 2:
                pass
            else:
                colsChecked.append(cols[i].replace(",", "."))
        data.append({
            'year': int(colsChecked[0]),
            'month': int(colsChecked[1]),
            'temp': np.array([float(x) for x in colsChecked[2:]])
        })
    return data


def get_avg_temp(data, year=None, month=None) -> float:
    if year and month:
        data = np.concatenate(
            [cel['temp'] for cel in data if cel['year'] == year and cel['month'] == month], axis=0)
    elif year:
        data = np.concatenate([cel['temp']
                              for cel in data if cel['year'] == year], axis=0)
    elif month:
        data = np.concatenate([cel['temp']
                              for cel in data if cel['month'] == month], axis=0)

    return sum(data)/len(data)
