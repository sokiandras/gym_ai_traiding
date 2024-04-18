import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import datetime
import tkinter as tk
from tkinter import filedialog



def save_graph(graph, filename):
    graph_folder = "D:\\Egyetem\\Diplomamunka\\logs\\Backtest_graphs"
    if not os.path.exists(graph_folder):
        os.makedirs(graph_folder)
    graph_file = os.path.join(graph_folder, filename)
    graph.savefig(graph_file)




def add_arrow(data, ax, date, action, cost_or_income):  # a cost_or_income nincs használatban most (de lehetne igazából)
    if action == 'Buy':
        arrow_style = 'arc3'
        index = data.index[data['Time'] == date][0]
        cost = int(data.loc[index, 'Cost'])
        label = f"Buy: {cost}$"
        y = data.loc[index, 'Cost']
        y_offset = 1
        ax.annotate(label, xy=(date, 1), xytext=(date, 0), arrowprops=dict(facecolor='green', shrink=0.05, connectionstyle=arrow_style))

    if action == 'sell':
        arrow_style = 'arc3'
        index = data.index[data['Time'] == date][0]
        income = int(data.loc[index, 'Income'])
        label = f"Sell: {income}$"
        y = data.loc[index, 'Income']
        y_offset = -1
        ax.annotate(label, xy=(date, 0), xytext=(date, 1), arrowprops=dict(facecolor='red', shrink=0.05, connectionstyle=arrow_style))




def make_graph(csv_file):
    data = pd.read_csv(csv_file)

    data['Time'] = pd.to_datetime(data['Time'], format = '%Y-%m-%d %H')
    #dates = data['Time'].dt.to_pydatetime()
    dates = data['Time']


    # Rotate x-axis labels for better readability
    # plt.xticks(rotation=45)

    fig, axs = plt.subplots(4, 1, sharex=True)

    #subplots:

    # Net worth plot
    axs[0].plot(dates, data['Net worth'], label ='Net worth')
    axs[0].set_title('Net Worth')
    axs[0].grid(True)


    for index, row in data.iterrows():
        action = row['Type']
        if row['Possibility'] == 1:
            if action in ['Buy', 'sell']:
                cost_or_income = row['Cost'] if action == 'Buy' else row['Income']
                add_arrow(data, axs[1], dates.iloc[index], action, cost_or_income)



    # Current price plot
    axs[2].plot(dates, data['Current price'], label='Current Price')
    axs[2].set_title('Current Price')
    axs[2].grid(True)

    # News scores plot
    axs[3].scatter(dates, data['News'], label ='News scores')
    axs[3].set_title('News Scores')
    axs[3].grid(True)

    # Format x-axis to display dates
    for ax in axs:
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # set the locations of the x-ticks
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))  # set the locations of the minor x-ticks
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # set the format of the x-ticks
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)



    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Set labels and title
    plt.xlabel('Date')
    plt.ylabel('Price/Score')
    plt.title('News Scores')

    # Add legend
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    #Save the plot
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    graph_filename = f'backtest_graph_{timestamp}.png'
    save_graph(fig, graph_filename)








def load_data_for_recreate_graph():
    root = tk.Tk()
    root.wm_withdraw()
    base_folder = "D:\Egyetem\Diplomamunka\logs\Backtests"
    data_path = filedialog.askopenfilename(initialdir=base_folder, filetypes = (("CSV Files","*.csv"),))

    if data_path is None:
        print("\nNo csv file has been chosen")
        return None

    return data_path



def recreate_graph():
    data = load_data_for_recreate_graph()
    if data is not None:
        make_graph(data)
    else:
        print("Data from csv is empty")
        return -1



#make_graph()
#recreate_graph()