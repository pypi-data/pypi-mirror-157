import numpy as np
from bashplotlib.histogram import plot_hist
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, output_notebook
import ipywidgets as widgets
from IPython.display import display, clear_output
from  plotly.offline import iplot
import plotly as py 
import plotly.tools as tls 
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from statistics import mean
output_notebook()

class Calculator:
    def add_numbers(num1, num2):
        return num1 + num2

    def subtract_numbers(num1, num2):
        return num1 - num2

    def multiply_numbers(num1, num2):
        return num1 * num2

    def divide_numbers(num1, num2):
        return num1 / num2
    
    def p():
        arr = np.random.normal(size=1000, loc=0, scale=1)
        return plot_hist(arr, bincount=50)

