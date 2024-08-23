import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import random

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


def plot_interactive(model, catalogue, view='3-D (l-b-v)'):
    fig = go.Figure()

    if view == '3-D (l-b-v)':
        trace_func = go.Scatter3d
        layout = dict(scene=dict(xaxis_title="l", yaxis_title="b", zaxis_title="v"))
    elif view == 'l-b':
        trace_func = go.Scatter
        layout = dict(xaxis_title="l", yaxis_title="b", xaxis_autorange="reversed")
    elif view == 'l-v':
        trace_func = go.Scatter
        layout = dict(xaxis_title="l", yaxis_title="v", xaxis_autorange="reversed")
    elif view == 'b-v':
        trace_func = go.Scatter
        layout = dict(xaxis_title="b", yaxis_title="v")


    def add_trace(data, name, symbol):
        if view == '3-D (l-b-v)':
            return trace_func(
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
            )
        elif view == 'l-b':
            return trace_func(x=data['l'], y=data['b'], mode='markers', marker=dict(size=5, color=data['near_far_numeric'], colorscale='RdBu_r', symbol=symbol, opacity=0.8), name=name)
        elif view == 'l-v':
            return trace_func(x=data['l'], y=data['v'], mode='markers', marker=dict(size=5, color=data['near_far_numeric'], colorscale='RdBu_r', symbol=symbol, opacity=0.8), name=name)
        elif view == 'b-v':
            return trace_func(x=data['b'], y=data['v'], mode='markers', marker=dict(size=5, color=data['near_far_numeric'], colorscale='RdBu_r', symbol=symbol, opacity=0.8), name=name)

    fig.add_trace(add_trace(model['data'], f'Model: {model["name"]}', 'circle'))
    fig.add_trace(add_trace(catalogue['data'], f'Data: {catalogue["name"]}', catalogue['symbol']))

    fig.update_layout(
        height=800,
        width=800,
        title_text=f"{model['name']} {view} view",
        **layout
    )
    return fig


def main():
    st.title("3-D CMZ Models")

    catalogues = [
        {
            'name': 'Walker et al. (2024)',
            'data': preprocess_data(load_data('walker-catalogue.txt', sep=',')),
            'symbol': 'x'
        },
        {
            'name': 'Lipman et al. (2024)',
            'data': preprocess_data(load_data('lipman-catalogue.txt', sep=',')),
            'symbol': 'x'
        }
    ]

    model_files = [
        ('ellipse_resampled_300.txt', '\t', "Ellipse"),
        ('kdl_resampled_300.txt', '\t', "KDL"),
        ('sofue_resampled_300.txt', '\t', "Sofue"),
        ('molinari_resampled_300.txt', '\t', "Molinari")
    ]

    models = [
        {
            'name': name,
            'data': preprocess_data(load_data(file, sep))
        }
        for file, sep, name in model_files
    ]

    if all(catalogue['data'] is None for catalogue in catalogues) and all(model['data'] is None for model in models):
        st.error("No data files could be loaded. Please check if the data files are present in the 'data' folder.")
        return

    if 'selected_catalogue_index' not in st.session_state:
        st.session_state.selected_catalogue_index = random.randint(0, len(catalogues) - 1)

    col1, col2 = st.columns(2)

    with col1:
        selected_model_name = st.selectbox(
            "Select a model to view:",
            options=[model['name'] for model in models]
        )

    with col2:
        selected_catalogue_name = st.selectbox(
            "Select catalogue to display:",
            options=[catalogue['name'] for catalogue in catalogues],
            index=st.session_state.selected_catalogue_index
        )

    selected_model = next((model for model in models if model['name'] == selected_model_name), None)
    selected_catalogue = next((catalogue for catalogue in catalogues if catalogue['name'] == selected_catalogue_name), None)

    view_options = ['3-D (l-b-v)', 'l-b', 'l-v', 'b-v']
    selected_view = st.radio("Select view:", view_options, index=0)

    if selected_model and selected_catalogue:
        fig = plot_interactive(selected_model, selected_catalogue, view=selected_view)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Selected model or catalogue not found.")


if __name__ == "__main__":
    main()