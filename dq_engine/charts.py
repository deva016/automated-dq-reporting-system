# dq_engine/charts.py

import matplotlib.pyplot as plt
import pandas as pd
import os

def bar_chart(data: pd.Series, title: str, filename: str):
    plt.figure(figsize=(8,4))
    data.plot(kind="bar")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def line_chart(data: pd.Series, title: str, filename: str):
    plt.figure(figsize=(8,4))
    data.plot(kind="line")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def pie_chart(data: pd.Series, title: str, filename: str):
    plt.figure(figsize=(5,5))
    data.plot(kind="pie", autopct='%1.1f%%')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
