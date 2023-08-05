import easygui
import pandas as pd
import plotly.express as px


def get_file_path():
    # selection for files
    path = easygui.fileopenbox("Select the CSV file", "Open")
    return path


def read_file(path):
    # read the csv file
    df = pd.read_csv(path, header=0, names=["Time", "Pressure"])
    return df


def create_plot(df):
    # create the graph
    fig = px.line(df, x="Time", y="Pressure", title="Pressure Graph")
    return fig


def main():

    path = get_file_path()
    df = read_file(path)
    fig = create_plot(df)

    fig.show()


if __name__ == '__main__':
    main()
