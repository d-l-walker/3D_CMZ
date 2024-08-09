import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def load_data(path, sep='\t', names=['l', 'b', 'v', 'near_far']):
    try:
        full_path = os.path.join(current_dir, 'data', path)
        return pd.read_csv(full_path, sep=sep, header=None, names=names)
    except FileNotFoundError:
        st.error(f"Error: The file {path} was not found in the data folder.")
        return None

def preprocess_data(df):
    if df is None:
        return None
    df = df.copy()
    df['near_far_numeric'] = df['near_far'].map({'Near': 0, 'Far': 1})
    return df

def plot_interactive_3d(model, catalogue):
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter3d(
            x=model['data']['l'], y=model['data']['b'], z=model['data']['v'],
            mode='markers',
            marker=dict(
                size=6,
                color=model['data']['near_far_numeric'],
                colorscale='RdBu',
                symbol='circle',
                opacity=0.8,
                colorbar=dict(
                    title='Near/Far',
                    tickvals=[0, 1],
                    ticktext=['Near', 'Far']
                )
            ),
            name=f'Model {model["name"]}',
            hovertemplate='<b>Model Point</b><br>l: %{x:.2f}<br>b: %{y:.2f}<br>v: %{z:.2f}<extra></extra>'
        )
    )
    
    fig.add_trace(
        go.Scatter3d(
            x=catalogue['l'], y=catalogue['b'], z=catalogue['v'],
            mode='markers',
            marker=dict(
                size=6,
                color=catalogue['near_far_numeric'],
                colorscale='RdBu',
                symbol='x',
                opacity=0.8
            ),
            name='Catalogue',
            hovertemplate='<b>Catalogue Point</b><br>l: %{x:.2f}<br>b: %{y:.2f}<br>v: %{z:.2f}<extra></extra>'
        )
    )
    
    fig.update_layout(
        scene=dict(
            xaxis_title='l',
            yaxis_title='b',
            zaxis_title='v',
            xaxis_autorange="reversed",
            bgcolor='rgb(240,240,240)'
        ),
        height=700,
        width=800,
        title=dict(
            text=f"3D Model Comparison - {model['name']}",
            x=0.5,
            y=0.95,
            font=dict(size=24)
        ),
        legend=dict(
            x=0.85,
            y=0.95,
            bgcolor='rgba(255,255,255,0.5)'
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )
    
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(args=[{'scene.camera.eye': {'x': 1.25, 'y': 1.25, 'z': 1.25}}],
                         label="Isometric",
                         method="relayout"),
                    dict(args=[{'scene.camera.eye': {'x': 0, 'y': 0, 'z': 2}}],
                         label="Top",
                         method="relayout"),
                    dict(args=[{'scene.camera.eye': {'x': 2, 'y': 0, 'z': 0}}],
                         label="Side",
                         method="relayout")
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.05,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )
    
    return fig

def main():
    st.title("3D Model Comparison")

    catalogue = preprocess_data(load_data('updated-catalogue.txt', sep=','))

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
