import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

def load_data(path, sep='\t', names=['l', 'b', 'v', 'near_far']):
    try:
        return pd.read_csv(path, sep=sep, header=None, names=names)
    except FileNotFoundError:
        st.error(f"Error: The file {path} was not found. Please check if the file exists in the 'data' folder.")
        return None

def preprocess_data(df):
    if df is None:
        return None
    df = df.copy()
    df['near_far_numeric'] = df['near_far'].map({'Near': 0, 'Far': 1})
    return df

def plot_interactive_3d(model, catalogue):
    fig = go.Figure()
    
    # Add model data
    fig.add_trace(
        go.Scatter3d(
            x=model['data']['l'], y=model['data']['b'], z=model['data']['v'],
            mode='markers',
            marker=dict(
                size=5,
                color=model['data']['near_far_numeric'],
                colorscale='RdBu_r',
                symbol='circle',
                opacity=0.8
            ),
            name=f'Model {model["name"]}'
        )
    )
    
    # Add catalogue data
    fig.add_trace(
        go.Scatter3d(
            x=catalogue['l'], y=catalogue['b'], z=catalogue['v'],
            mode='markers',
            marker=dict(
                size=5,
                color=catalogue['near_far_numeric'],
                colorscale='RdBu_r',
                symbol='x',
                opacity=0.8
            ),
            name='Catalogue'
        )
    )
    
    fig.update_layout(
        scene=dict(xaxis_autorange="reversed"),
        height=800,
        width=800,
        title_text=f"3D Model Comparison - {model['name']}"
    )
    return fig

def main():
    st.title("3D Model Comparison")

    catalogue = preprocess_data(load_data(os.path.join('data', 'updated-catalogue.txt'), sep=','))

    model_files = [
        ('molinari_resampled_300.txt', '\t', "Molinari"),
        ('sofue_resampled_300.txt', '\t', "Sofue"),
        ('kdl_resampled_300.txt', '\t', "KDL"),
        ('ellipse_resampled_300.txt', '\t', "Ellipse")
    ]

    models = [
        {
            'name': name,
            'data': preprocess_data(load_data(os.path.join('data', file), sep))
        }
        for file, sep, name in model_files
    ]

    if catalogue is None and all(model['data'] is None for model in models):
        st.error("No data files could be loaded. Please check if the data files are present in the 'data' folder.")
        return

    selected_model_name = st.selectbox(
        "Select a model to view:",
        options=[model['name'] for model in models]
    )

    selected_model = next((model for model in models if model['name'] == selected_model_name), None)

    if selected_model:
        fig = plot_interactive_3d(selected_model, catalogue)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Selected model not found.")

if __name__ == "__main__":
    main()
