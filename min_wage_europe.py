import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

def draw_plot():
    # Set default fonts
    plt.rcParams['font.family'] = 'fantasy'
    plt.rcParams['font.fantasy'] = ['Impact']

    # Set background colour
    plt.rcParams['axes.facecolor'] = 'lightsteelblue'

    # Set style
    plt.style.use('Solarize_Light2')

    # Import data of min wages 2016-2021
    df=pd.read_csv('earn_mw_cur_1_Data.csv', encoding='latin1')

    # Clean the data
    df.drop(['Flag and Footnotes'], axis=1, inplace=True)
    df.drop(df[df['GEO'] == 'United States'].index, inplace=True)
    df.replace(to_replace="Germany (until 1990 former territory of the FRG)", value="Germany", inplace=True)
    df.replace(to_replace=':', value='NaN', inplace=True)
    df.sort_values('GEO', inplace=True)
    df.rename(columns={'GEO':'name'}, inplace=True)
    df['Value']=df['Value'].astype(float)
    df['Value']=df['Value'].round()
    df.dropna(axis=0, how='any', inplace=True)
    df['Value']=df['Value'].apply(lambda x: int(x))

    # Show only second half of 2020
    df.drop(df[df['TIME'] != '2020S2'].index, inplace=True)

    # Load base map
    world = gpd.read_file('naturalearth_lowres')

    # Customize column names for merging with DataFrame
    world.rename(columns={'name':'country_name'}, inplace=True)

    # Set better projection
    world = world.to_crs(epsg=3035)

    # Filter for Europe
    world = world[(world['continent'] == 'Europe') | (world['country_name'] == 'Turkey')]

    # Plot base map
    base = world.plot(color='dimgray', figsize=(16,9), edgecolor='black',linewidth=.2)

    # Merge the map and data
    table = world.merge(df, right_on='name', left_on='country_name')

    # Import data that shows coordinates of centres of all countries
    countrycentre=pd.read_csv('countriescentre.csv', encoding='latin1')

    # Customize for merging
    countrycentre.replace(to_replace='Czech Republic', value='Czechia', inplace=True)

    # Merge DataFrames to show minimum wages and coordinates of countries in Europe
    centre_with_minwages = df.merge(countrycentre, on='name', how='left')

    # Create geopandas DataFrame
    centre_with_minwages_gdf = gpd.GeoDataFrame(centre_with_minwages, crs=4326,
                        geometry=gpd.points_from_xy(x=centre_with_minwages.longitude,
                                                     y=centre_with_minwages.latitude))

    # Suit projection to base map
    centre_with_minwages_gdf = centre_with_minwages_gdf.to_crs(epsg=3035)

    # Optional markers on map indicates countries:
    # centre_with_minwages_gdf.plot(marker='.', markersize=3 ,color='red', ax=base)

    # Plot ready map
    table.plot(ax=base, column='Value', vmax=2000, vmin= 300, cmap='RdBu', edgecolor='black', linewidth=.4, legend=True,
              # Customize appearance of legend
               legend_kwds={'location': 'bottom', 'spacing': 'proportional',
                            'shrink': .50, 'pad': -0.09,
                            'aspect': 50}
               )

    # Annotating minimum wages over each countries
    for idx, row in centre_with_minwages_gdf.iterrows():
        txt = plt.text(x=row.geometry.x, y=row.geometry.y, s=row['Value'],
                       fontsize=(row['Value'] ** 0.35), color='white',
                       family='arial', rotation=row['longitude']/4,
                     fontproperties={'weight':1000, 'variant':'small-caps'}, wrap=True,
                      horizontalalignment='center', verticalalignment='center')
        # Set black border color of each characters for better readability
        txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='black')])

    # Add title to the plot
    title = plt.text(x=4.5*1e6, y=4.5*1e6, s='Minimum wages (Euro / month)',
                     fontsize=28, color='white', horizontalalignment='center', verticalalignment='center')

    # Set black border color of each characters for better readability
    title.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='black')])

    # Remove axes
    plt.xticks([])
    plt.yticks([])

    # Zoom the area of Europe
    bounds = centre_with_minwages_gdf.geometry.bounds
    plt.xlim([bounds.minx.min()-0.5*1e6, bounds.maxx.max()+0.3*1e6])
    plt.ylim([bounds.miny.min()-0.5*1e6, bounds.maxy.max()+0.7*1e6])

    # Plot the map
    plt.tight_layout()
    plt.show()


