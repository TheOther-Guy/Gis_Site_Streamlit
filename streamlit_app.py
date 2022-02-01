
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point
import geemap.foliumap as geemap

gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'


df = gpd.read_file("Sample (4).kml", driver='KML')

df = df.to_crs('ESRI:102009')

df_exploded = df.explode(column='geometry', ignore_index=True)

df_exploded.dropna(inplace=True)

df_exploded.dropna(inplace=True)

df_exploded = df_exploded.reset_index()

df_exploded.rename(columns={'index':'id'}, inplace=True)

indx = []  # for A1, A3
sequ = []  # for seg order
pxy0 = []  # from-point
pxy1 = []  # to-point
for ix,geom in zip(df_exploded.id, df_exploded.geometry):
    num_pts = len(geom.exterior.xy[0])
    #print(ix, "Num points:", num_pts)
    old_xy = []
    for inx, (x,y) in enumerate(zip(geom.exterior.xy[0],geom.exterior.xy[1])):
        if (inx==0):
            # first vertex is the same as the last
            pass
        else:
            indx.append(ix)
            sequ.append(inx)
            pxy0.append(Point(old_xy))
            pxy1.append(Point(x,y))
        old_xy = (x,y)

# Create new geodataframe 
pgon_segs  = gpd.GeoDataFrame({"poly_id": indx,
                 "vertex_id": sequ,
                 "fr_point": pxy0,
                 "to_point": pxy1}, geometry="to_point")
# Compute segment lengths
# Note: seg length is Euclidean distance, ***not geographic***
pgon_segs["seg_length"] = pgon_segs.apply(lambda row: row.fr_point.distance(row.to_point), axis=1)


pgon_segs['line'] = pgon_segs.apply(lambda row: LineString([row['fr_point'], row['to_point']]), axis=1)

pgon_segs.rename(columns={'line':'geometry'}, inplace=True)

pgon_segs = pgon_segs.set_geometry('geometry')

pgon_segs = pgon_segs.set_crs("ESRI:102009")

nodes_df = pgon_segs[['poly_id','vertex_id','fr_point','to_point']]

nodes_gdf = gpd.GeoDataFrame(nodes_df, geometry='fr_point', crs=pgon_segs.crs)

pgon_segs.drop(columns=['fr_point','to_point'], inplace=True)

pgon_segs['seg_length'] = round(pgon_segs['seg_length'], 1)





