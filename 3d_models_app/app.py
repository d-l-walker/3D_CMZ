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
        layout = dict(
            scene=dict(
                xaxis_title="l",
                yaxis_title="b",
                zaxis_title="v",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='cube'
            )
        )
    elif view == 'l-b':
        trace_func = go.Scatter
        layout = dict(
            xaxis_title="l",
            yaxis_title="b",
            xaxis_autorange="reversed"
        )
    elif view == 'l-v':
        trace_func = go.Scatter
        layout = dict(
            xaxis_title="l",
            yaxis_title="v",
            xaxis_autorange="reversed"
        )
    elif view == 'b-v':
        trace_func = go.Scatter
        layout = dict(
            xaxis_title="b",
            yaxis_title="v"
        )

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
        elif view in ['l-b', 'l-v', 'b-v']:
            x = data['l'] if 'l' in view else data['b']
            y = data['v'] if 'v' in view else data['b']
            return trace_func(
                x=x, y=y,
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

    fig.add_trace(add_trace(model['data'], f'Model: {model["name"]}', 'circle'))
    fig.add_trace(add_trace(catalogue['data'], f'Data: {catalogue["name"]}', catalogue['symbol']))

    all_data = pd.concat([model['data'], catalogue['data']])
    l_range = [all_data['l'].min(), all_data['l'].max()]
    b_range = [all_data['b'].min(), all_data['b'].max()]
    v_range = [all_data['v'].min(), all_data['v'].max()]

    layout.update(
        xaxis=dict(range=l_range if 'l' in view else b_range),
        yaxis=dict(range=b_range if view == 'l-b' else v_range)
    )

    if view == '3-D (l-b-v)':
        layout['scene'].update(
            xaxis=dict(range=l_range),
            yaxis=dict(range=b_range),
            zaxis=dict(range=v_range)
        )

    fig.update_layout(
        height=900,
        title_text=f"{model['name']} {view} view",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=0, r=0, t=30, b=100),
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
            "Select a model to display:",
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
    selected_view = st.radio("Select view:", view_options, index=0, horizontal=True)

    if selected_model and selected_catalogue:
        fig = plot_interactive(selected_model, selected_catalogue, view=selected_view)
        
        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=30, b=0),
            height=900,
        )

        st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
    else:
        st.error("Selected model or catalogue not found.")

    st.markdown("""
    This interactive tool shows four models of the 3-D geometry of the CMZ:
    * A closed, vertically-oscillating elliptical orbit with constant angular momentum (Ellipse; [Walker et al. 2024](#))
    * An open, eccentric orbit (KDL; [Kruijssen et al. 2024](#))
    * Two nuclear spiral arms (Sofue; [Sofue et al. 1995](#))
    * A closed, vertically-oscillating elliptical orbit with constant orbital velocity (Molinari; [Molinari et al. 2011](#))

    Along with two cloud catalogues from [Lipman et al. (2024)](#) and [Walker et al. (2024)](#).

    For more information on the 3-D CMZ project and associated data, code, and publications, please visit [centralmolecularzone.github.io/3D_CMZ/](https://centralmolecularzone.github.io/3D_CMZ/)
    """)

if __name__ == "__main__":
    main()