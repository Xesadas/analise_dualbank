import pandas as pd
import numpy as np
import dash
import openpyxl

path = 'stores.xlsx'
df = pd.read_excel(path, sheet_name='Sheet1', engine='openpyxl')