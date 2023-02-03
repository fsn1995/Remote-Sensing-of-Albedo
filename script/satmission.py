# %%
import altair as alt
# from altair_saver import save
import pandas as pd
from datetime import date
import plotly.express as px



# %%
df = pd.read_excel("bandtransform.xlsx", sheet_name="all")
df = df.dropna()

base = alt.Chart(df).encode(
    alt.X('wavelength (nm) 1:Q', scale=alt.Scale(domain=(400, 2400)), title='wavelength (nm)'),
    x2='wavelength (nm) 2',
    y='satellite',
)
bars = base.mark_bar().encode(
    # x='wavelength (nm) 1',
    # x2='wavelength (nm) 2',
    # y='satellite',
    color = alt.Color('color', scale=None),
    tooltip=['satellite', 'band name', 'sr band name', 'wavelength (nm) 1', 'wavelength (nm) 2', 'resolution (m)']
).properties(
    width=900,
    height=200
)

text = base.mark_text(
    # align='left',
    baseline='middle',
    dy=7,  # Nudges text to right so it doesn't appear on top of the bar,
    color = 'white',
    angle=270,
    font='Arial',
    fontSize=13,
    fontWeight='bold'
).encode(
    text='sr band name:N'
)
chart = (bars + text).interactive().configure_axis(
# chart = bars.interactive().configure_axis(    
    labelFontSize=20,
    titleFontSize=20,
    labelFont="Arial",
    titleFont="Arial"
)
chart
# chart.save('print/satelliteSpectra.pdf')
# chart.save('print/satelliteSpectra.html')

# %%
df = pd.read_excel("bandtransform.xlsx", sheet_name="satmission")

df['end_time_plot'] = pd.to_datetime(df['end_time'])
df['end_time'] = pd.to_datetime(df['end_time'])
df.end_time_plot[pd.isnull(df.end_time_plot)] = date.today()
df.fillna('present', inplace=True)
fig = px.timeline(df, x_start="start_time", x_end="end_time_plot", y="satellite", 
                  color="satellite" ,width=1000, height=220, template="plotly", hover_data={'start_time':True, 'end_time':True, 'end_time_plot':False})
fig.update_layout(
    showlegend=False,
    font=dict(
        size=20,
        family="Arial",
        color='black'
    ),
    # title_font_color='black',
    margin=dict(
        l=5,
        r=5,
        b=5,
        t=5,
        # pad=4
    ),
    # xaxis_title="time"
)
fig.add_vline(x=pd.to_datetime("1984-03-16"), line_width=2, line_dash="dash", line_color="black")
fig.add_vline(x=pd.to_datetime("2021-01-01"), line_width=2, line_dash="dash", line_color="black")
# fig.add_vline(x=pd.to_datetime("2017-03-28"), line_width=2, line_dash="dash", line_color="black")
fig.add_vline(x=pd.to_datetime("2019-01-01"), line_width=2, line_dash="dash", line_color="black")
# fig.update_yaxes(automargin=True)
fig.show()
# fig.write_image("print/satelliteMission.svg")
fig.write_image("print/satelliteMission.png")



