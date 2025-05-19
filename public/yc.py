# import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px

# df_col = pd.read_excel('./asset/data/data1.xls')
df = pd.read_csv('./asset/data/KC_495_LLR_ATRCTN_2023.csv')
df = df[df['SIGNGU_NM']=='영천시']
df = df[(df['CL_NM']!='항공사/여행사') & (df['CL_NM'] != '관광안내소/매표소')]
df['CL_NM'].unique()

df[df['CL_NM'] == 'N']