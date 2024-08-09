import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_data(path, sep='\t', names=['l', 'b', 'v', 'near_far']):
    return pd.read_csv(path, sep=sep, header=None, names=names)

def preprocess_data(df):
    df = df.copy()
    df['near_far_numeric'] = df['near_far'].map({'Near': 0, 'Far': 1})
    return df

def plot_interactive_3d(models, catalogue):
    fig = make_subplots(
        rows=1, cols=len(models),
        specs=[[{'type': 'scene'}]*len(models)],
        subplot_titles=[model['name'] for model in models]
    )
    for i, model in enumerate(models, start=1):
        model_data = model['data']
        for data, name, symbol in [(model_data, f'Model {model["name"]}', 'circle'),
                                   (catalogue, 'Catalogue', 'x')]:
            fig.add_trace(
                go.Scatter3d(
                    x=data['l'], y=data['b'], z=data['v'],
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=data['near_far_numeric'],
                        colorscale='RdBu_r',
                        symbol=symbol,
                        opacity=0.8
                    ),
                    name=name
                ),
                row=1, col=i
            )
        fig.update_scenes(xaxis_autorange="reversed", row=1, col=i)
    fig.update_layout(height=800, width=800*len(models), title_text="3D Model Comparison")
    return fig

def main():
    st.title("3D Model Comparison")

    # Load and preprocess catalogue data
    catalogue = preprocess_data(load_data('updated-catalogue.txt', sep=','))

    # Load and preprocess model data
    model_files = [
        ('molinari_resampled_300.txt', '\t', "Molinari"),
        ('sofue_resampled_300.txt', '\t', "Sofue"),
        ('kdl_resampled_300.txt', '\t', "KDL"),
        ('ellipse_resampled_300.txt', '\t', "Ellipse")
    ]

    models = [
        {
            'name': name,
            'data': preprocess_data(load_data(file, sep))
        }
        for file, sep, name in model_files
    ]

    # Create and display the interactive 3D plot
    fig = plot_interactive_3d(models, catalogue)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
