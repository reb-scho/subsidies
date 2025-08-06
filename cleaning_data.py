import pandas as pd

def load_and_clean(file_path, verbose=False):
  df_dict = pd.read_excel(file_path, sheet_name=None)

  #check sheets
  if verbose:
    print(f"No. of sheets: {len(df_dict)}")

  for sheet, df in df_dict.items():
    if verbose:
      print(f"Sheet name: {sheet}")
      print(df.head())
  
  #clean 1st sheet
  subs_raw = pd.read_excel(file_path, sheet_name="Subsidies by country")
  new_columns = subs_raw.iloc[3].tolist()
  subs_clean = pd.read_excel(file_path, sheet_name='Subsidies by country', skiprows=4)
  subs_clean.columns = new_columns
  
  #split 1st sheet into 2 dataframes
  nan_row_index = subs_clean[subs_clean.isna().all(axis=1)].index[0] #find index of row where all cells are NaN
  
  global_df = subs_clean.iloc[:nan_row_index] #.iloc selects rows and columns by index, they can be sliced
  country_df = subs_clean.iloc[nan_row_index+1:] #use slice syntax [start:stop:step]
  
  #clean 1st dataframe
  clean_column_names = []
  
  for i, col in enumerate(global_df.columns): #enumerate returns index, column name
    if pd.isna(col):
      clean_column_names.append(f"col_{i}")
    elif isinstance(col, float) and col.is_integer():
      clean_column_names.append(str(int(col)))
    else:
      clean_column_names.append(str(col))
  
  global_df.columns = clean_column_names
  global_df = global_df.drop(global_df.columns[1], axis=1)
  global_df.rename(columns={'col_0': 'Product'}, inplace=True)
  
  #separate indiviudal and aggregate products
  global_product_df = global_df[global_df["Product"] != "Total"].copy()
  global_total_df = global_df[global_df["Product"] == "Total"].copy()
  
  #melt
  global_product_df = pd.melt(global_product_df, id_vars=["Product"], var_name="Year", value_name="Value (M USD)")
  global_total_df = pd.melt(global_total_df, id_vars=["Product"], var_name="Year", value_name="Value (M USD)")
  
  #change value from M to B
  global_product_df['Value (M USD)'] /= 1000
  global_product_df.rename(columns={'Value (M USD)': 'Value (B USD)'}, inplace=True) 
  
  global_total_df['Value (M USD)'] /= 1000
  global_total_df.rename(columns={'Value (M USD)': 'Value (B USD)'}, inplace=True) 
    
  #clean 2nd dataframe
  columns = list(country_df.columns)
  columns[0] = "Country"
  columns[1] = "Product"
  
  country_df.columns = columns
  country_df.iloc[0]
  country_df = country_df.drop(country_df.index[0]) 
  
  clean_column_names = []
  
  for i, col in enumerate(country_df.columns): #enumerate returns index, column name
    if isinstance(col, float) and col.is_integer():
      clean_column_names.append(str(int(col)))
    else:
      clean_column_names.append(str(col))
  
  country_df.columns = clean_column_names
  
  #separate indiviudal and aggregate products
  country_product_df = country_df[country_df["Product"] != "Total"].copy()
  country_total_df = country_df[country_df["Product"] == "Total"].copy()
  
  #melt
  country_product_df = pd.melt(country_product_df, id_vars=["Country", "Product"], var_name="Year", value_name="Value (M USD)")
  country_total_df = pd.melt(country_total_df, id_vars=["Country", "Product"], var_name="Year", value_name="Value (M USD)")
  
  #change value from M to B
  country_product_df['Value (M USD)'] /= 1000
  country_product_df.rename(columns={'Value (M USD)': 'Value (B USD)'}, inplace=True) 
  
  country_total_df['Value (M USD)'] /= 1000
  country_total_df.rename(columns={'Value (M USD)': 'Value (B USD)'}, inplace=True) 
  
  return global_product_df, global_total_df, country_product_df, country_total_df
