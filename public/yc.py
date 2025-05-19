import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px

df_col = pd.read_excel('./asset/data/data1.xls')
df = pd.read_csv('./asset/data/KC_495_LLR_ATRCTN_2023.csv')
df[df['SIGNGU_NM'] == '영천시']
