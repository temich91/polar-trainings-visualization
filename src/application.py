from dash import Dash, html, dcc, callback, Input, Output
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px

# just test application
df = pd.read_csv("../csv_export/8004137382.csv", skiprows=2)

app = Dash()
app.layout = [
    html.H2(children="Test Dash App"),
    html.Hr(),
    dag.AgGrid(
        rowData=df.to_dict(orient="records"),
        columnDefs=[{"field": i} for i in df.columns]
    ),
    html.Hr(),
    dcc.Graph(figure=px.line(df, x="Time", y="HR (bpm)"))
]

if __name__ == "__main__":
    app.run(debug=True)
