"""
International Art Price Effects Map Visualization
-------------------------------------------------
This script creates an interactive map using Plotly showing international price effects
between countries based on art market transaction data.

Features:
- Country nodes located at approximate geographical coordinates.
- Directed connections representing flow between artist country and sale country.
- Line thickness (width) scaled according to absolute effect percentage (|foreign_effect_percentage|).
- Line color mapped by statistical significance (p-value / -log10(p-value)).
- Interactive hover tooltips detailing countries, effect magnitude, direction, and p-value.
"""

import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# 1. Input Data
csv_data = """artist_country,foreign_sale_country,foreign_effect_percentage,p_value
Austria,Germany,-55.27362421405948,2.5085181490853075e-13
Austria,Switzerland,26.777596184246576,0.027457011485043502
Austria,United Kingdom,12.92923099329034,0.030025629076170374
Brazil,United States,354.09939035711807,2.051855408224779e-40
China,United Kingdom,-16.081365383772404,0.2148201990233154
China,United States,-47.44787189893338,0.036591803434136955
France,Germany,214.29340780241907,0.2290408501400859
France,Switzerland,-68.2711306115556,2.7085386792927393e-48
France,United Kingdom,-15.320418230796582,0.0644223672244893
France,United States,-28.63889125688558,0.03443895210199112
Germany,Austria,61.6832685270615,2.7405698156106504e-05
Germany,France,74.21097322751173,0.08566320209232231
Germany,Italy,73.18542696214125,0.5104157832325147
Germany,Netherlands,-12.698285417113182,0.7606904126454517
Germany,Switzerland,9.821096503805848,0.8091041228968463
Germany,United Kingdom,70.16976377560273,0.01968152224715769
Germany,United States,67.50186450991534,0.05637984807210186
India,United States,-33.31396067154637,0.5662874654747481
Italy,France,-0.6555225418889221,0.9613645927553774
Italy,Germany,61.34705863718792,0.033807711704890976
Italy,Switzerland,18.897579850443364,0.5835077161233364
Italy,United Kingdom,67.95815887530645,0.0028537356936508074
Italy,United States,8.329666282788036,0.46073980436519646
Switzerland,Germany,-6.493643298160695,0.6861573636541416
Switzerland,United Kingdom,27.05953679589994,0.32675310004076064
Switzerland,United States,28.597589090212672,0.4128317131997695
United Kingdom,France,11.448645074417833,0.7055152787966559
United Kingdom,Germany,38.98964115572735,0.07945727639613746
United Kingdom,Switzerland,102.58938987667645,1.0518599765725589e-05
United Kingdom,United States,-0.7329205399766477,0.9001337706391863
United States,Austria,195.51507670440546,7.324039086591602e-38
United States,France,-32.12106531935483,0.012569433283922264
United States,Germany,-72.645748109409,7.935118890831581e-05
United States,Italy,-57.59706355757306,0.043091125395321755
United States,Netherlands,-62.506781387147605,0.00042298537780130756
United States,Sweden,39.440272828408126,0.09265794257168723
United States,Switzerland,-53.44118158979623,0.01105887018703267
United States,United Kingdom,-1.5105054155771926,0.6904245645953457"""

df = pd.read_csv(io.StringIO(csv_data))

# 2. Country Centroid Coordinates (Latitude, Longitude)
COUNTRY_COORDS = {
    'Austria': (47.5162, 14.5501),
    'Brazil': (-14.2350, -51.9253),
    'China': (35.8617, 104.1954),
    'France': (46.2276, 2.2137),
    'Germany': (51.1657, 10.4515),
    'India': (20.5937, 78.9629),
    'Italy': (41.8719, 12.5674),
    'Netherlands': (52.1326, 5.2913),
    'Sweden': (60.1282, 18.6435),
    'Switzerland': (46.8182, 8.2275),
    'United Kingdom': (55.3781, -3.4360),
    'United States': (37.0902, -95.7129)
}

def create_price_effects_map(data_df):
    fig = go.Figure()

    # Scale line widths proportionally to absolute effect percentage
    abs_effect = data_df['foreign_effect_percentage'].abs()
    min_w, max_w = 1.0, 7.0
    scaled_widths = min_w + (abs_effect - abs_effect.min()) / (abs_effect.max() - abs_effect.min() + 1e-6) * (max_w - min_w)

    # Add lines connecting countries
    for idx, row in data_df.iterrows():
        src, dst = row['artist_country'], row['foreign_sale_country']
        if src not in COUNTRY_COORDS or dst not in COUNTRY_COORDS:
            continue

        lat1, lon1 = COUNTRY_COORDS[src]
        lat2, lon2 = COUNTRY_COORDS[dst]

        p_val = row['p_value']
        effect = row['foreign_effect_percentage']
        width = scaled_widths[idx]

        # Categorize color by significance level (p-value threshold)
        if p_val < 0.001:
            color = 'rgb(178, 24, 43)'    # Dark Red (p < 0.001)
        elif p_val < 0.05:
            color = 'rgb(239, 138, 98)'   # Coral / Orange (p < 0.05)
        elif p_val < 0.10:
            color = 'rgb(253, 219, 199)'  # Light Orange (p < 0.10)
        else:
            color = 'rgb(180, 180, 180)'  # Light Grey (Not significant)

        fig.add_trace(go.Scattergeo(
            locationmode='country names',
            lon=[lon1, lon2],
            lat=[lat1, lat2],
            mode='lines',
            line=dict(width=width, color=color),
            opacity=0.8,
            hoverinfo='text',
            text=f"<b>{src} → {dst}</b><br>"
                 f"Effect: {effect:+.2f}%<br>"
                 f"p-value: {p_val:.2e}"
        ))

    # Add Country Nodes
    all_countries = set(data_df['artist_country']).union(set(data_df['foreign_sale_country']))
    node_lats = [COUNTRY_COORDS[c][0] for c in all_countries if c in COUNTRY_COORDS]
    node_lons = [COUNTRY_COORDS[c][1] for c in all_countries if c in COUNTRY_COORDS]
    node_names = [c for c in all_countries if c in COUNTRY_COORDS]

    fig.add_trace(go.Scattergeo(
        lon=node_lons,
        lat=node_lats,
        mode='markers+text',
        text=node_names,
        textposition="top center",
        marker=dict(size=9, color='darkblue', line=dict(width=1, color='white')),
        hoverinfo='text'
    ))

    # Layout configuration
    fig.update_layout(
        title=dict(
            text="<b>International Price Effects Map</b><br>"
                 "<sup>Line width = |Effect %| | Red = High Significance (p < 0.001), Orange = Moderate (p < 0.05), Grey = Insignificant</sup>",
            x=0.5
        ),
        showlegend=False,
        geo=dict(
            projection_type='equirectangular',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            coastlinecolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(235, 245, 255)',
        ),
        margin=dict(l=20, r=20, t=80, b=20)
    )

    return fig

if __name__ == '__main__':
    fig = create_price_effects_map(df)
    # To view in browser:
    fig.show()
    # To save as interactive HTML file:
    fig.write_html("price_effects_map.html")