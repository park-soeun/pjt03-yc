import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px


# data = pd.read_csv('../../data/경상북도_관광지 현황_20250101.csv')
df_col = pd.read_excel('../../data/data1.xls')
df = pd.read_csv('../../data/KC_495_LLR_ATRCTN_2023.csv')
df = df[df['SIGNGU_NM'] == '영천시']
df['CL_NM'].unique()

df