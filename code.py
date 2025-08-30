import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

value_label = "Value (Real 2023 USD, billions)"

#clean data
def load_and_clean(file_path, verbose=False):
    """Load and clean IEA fossil fuel subsidies data."""
    df_dict = pd.read_excel(file_path, sheet_name=None)

    if verbose:
        print(f"No. of sheets: {len(df_dict)}")
        for sheet, df in df_dict.items():
            print(f"Sheet name: {sheet}")
            print(df.head())

    #clean first sheet
    subs_raw = pd.read_excel(file_path, sheet_name="Subsidies by country")
    new_columns = subs_raw.iloc[3].tolist()
    subs_clean = pd.read_excel(file_path, sheet_name='Subsidies by country', skiprows=4)
    subs_clean.columns = new_columns

    nan_row_index = subs_clean[subs_clean.isna().all(axis=1)].index[0]

    global_df = subs_clean.iloc[:nan_row_index]
    country_df = subs_clean.iloc[nan_row_index + 1:]

    #clean global_df
    clean_column_names = []
    for i, col in enumerate(global_df.columns):
        if pd.isna(col):
            clean_column_names.append(f"col_{i}")
        elif isinstance(col, float) and col.is_integer():
            clean_column_names.append(str(int(col)))
        else:
            clean_column_names.append(str(col))
    global_df.columns = clean_column_names
    global_df = global_df.drop(global_df.columns[1], axis=1)
    global_df.rename(columns={'col_0': 'Product'}, inplace=True)

    global_product_df = global_df[global_df["Product"] != "Total"].copy()
    global_total_df = global_df[global_df["Product"] == "Total"].copy()

    global_product_df = pd.melt(global_product_df, id_vars=["Product"], var_name="Year", value_name="Value (M USD)")
    global_total_df = pd.melt(global_total_df, id_vars=["Product"], var_name="Year", value_name="Value (M USD)")

    global_product_df['Value (M USD)'] /= 1000
    global_product_df.rename(columns={'Value (M USD)': 'Value (B USD)'}, inplace=True)

    global_total_df['Value (M USD)'] /= 1000
    global_total_df.rename(columns={'Value (M USD)': 'Value (B USD)'}, inplace=True)

    #clean country_df
    columns = list(country_df.columns)
    columns[0] = "Country"
    columns[1] = "Product"
    country_df.columns = columns
    country_df = country_df.drop(country_df.index[0])

    clean_column_names = []
    for i, col in enumerate(country_df.columns):
        if isinstance(col, float) and col.is_integer():
            clean_column_names.append(str(int(col)))
        else:
            clean_column_names.append(str(col))
    country_df.columns = clean_column_names

    country_product_df = country_df[country_df["Product"] != "Total"].copy()
    country_total_df = country_df[country_df["Product"] == "Total"].copy()

    country_product_df = pd.melt(country_product_df, id_vars=["Country", "Product"], var_name="Year",
                                 value_name="Value (M USD)")
    country_total_df = pd.melt(country_total_df, id_vars=["Country", "Product"], var_name="Year",
                               value_name="Value (M USD)")

    country_product_df['Value (M USD)'] /= 1000
    country_product_df.rename(columns={'Value (M USD)': 'Value (B USD)'}, inplace=True)

    country_total_df['Value (M USD)'] /= 1000
    country_total_df.rename(columns={'Value (M USD)': 'Value (B USD)'}, inplace=True)

    country_elec_df = country_product_df[country_product_df["Product"] == "Electricity"].copy()
    country_fossil_df = country_product_df[country_product_df["Product"] != "Electricity"].copy()
    country_fossil_agg_df = country_fossil_df.groupby(["Country", "Year"])["Value (B USD)"].sum().reset_index()

    global_elec_df = global_product_df[global_product_df["Product"] == "Electricity"].copy()
    global_fossil_df = global_product_df[global_product_df["Product"] != "Electricity"].copy()
    global_fossil_agg_df = global_fossil_df.groupby("Year")["Value (B USD)"].sum().reset_index()

    return (global_product_df, global_total_df, 
            country_product_df, country_total_df,
            country_elec_df, country_fossil_df, country_fossil_agg_df,
            global_elec_df, global_fossil_df, global_fossil_agg_df)

#functions for plotting

def plot_fig1(global_elec_df, global_fossil_agg_df, value_label):
    plt.plot(global_elec_df["Year"], global_elec_df["Value (B USD)"], label="Electricity")
    plt.plot(global_fossil_agg_df["Year"], global_fossil_agg_df["Value (B USD)"], label="Fossil fuels")
    plt.xlabel("Year")
    plt.xticks(rotation=90)
    plt.ylabel(value_label)
    plt.title("Figure 1: Total global subsidies for fossil fuels and electricity")
    plt.grid()
    plt.legend()
    plt.show()

def plot_fig2(global_elec_df, global_fossil_agg_df, value_label):
    df_fossil = global_fossil_agg_df.copy()
    df_fossil["Product"] = "Fossil fuels"
    df_concat = pd.concat([df_fossil, global_elec_df], ignore_index=True)
    df_wide = df_concat.pivot(index="Year", columns="Product", values="Value (B USD)")
    df_wide.plot.area(stacked=True)
    plt.xlabel("Year")
    plt.ylabel(value_label)
    plt.title("Figure 2: Stacked Area Chart of electricity and fossil fuels")
    plt.legend(title="Category", loc="upper left")
    plt.show()

def plot_fig3(global_elec_df, global_fossil_df, value_label):
    plt.plot(global_elec_df["Year"], global_elec_df["Value (B USD)"], label="Electricity")
    for product in global_fossil_df["Product"].unique():
        df = global_fossil_df[global_fossil_df["Product"] == product]
        plt.plot(df["Year"], df["Value (B USD)"], label=product)
    plt.xlabel("Year")
    plt.xticks(rotation=90)
    plt.ylabel(value_label)
    plt.title("Figure 3: Total global subsidies for individual fossil fuels and electricity")
    plt.grid()
    plt.legend()
    plt.show()

def plot_fig4(global_product_df, value_label):
    df_wide = global_product_df.pivot(index="Year", columns="Product", values="Value (B USD)")
    df_wide.plot.area(stacked=True)
    plt.xlabel("Year")
    plt.ylabel(value_label)
    plt.title("Figure 4: Stacked Area Chart of electricity and fossil fuels")
    plt.legend(title="Category", loc="upper left")
    plt.show()

def plot_fig5(global_fossil_agg_df, global_elec_df, value_label):
    df_concat = pd.concat([global_fossil_agg_df.assign(Product="Fossil fuels"), global_elec_df], ignore_index=True)
    df_wide = df_concat.pivot(index="Year", columns="Product", values="Value (B USD)")
    df_norm = df_wide.div(df_wide.sum(axis=1), axis=0) * 100
    df_norm.plot.bar(stacked=True)
    plt.xlabel("Year")
    plt.ylabel("Percentage")
    plt.title("Figure 5: 100% stacked bar chart electricity and fossil fuels")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()

def plot_fig6(global_fossil_df, value_label):
    df_wide = global_fossil_df.pivot(index="Year", columns="Product", values="Value (B USD)")
    df_norm = df_wide.div(df_wide.sum(axis=1), axis=0) * 100
    df_norm.plot.bar(stacked=True)
    plt.xlabel("Year")
    plt.ylabel("Percentage")
    plt.title("Figure 6: 100% stacked bar chart of fossil fuel subsidies")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()

def plot_fig7(global_product_df, value_label):
    global_product_df.boxplot(column="Value (B USD)", by="Product")
    plt.xticks(rotation=90)
    plt.title("Figure 7: Global subsidies for electricity, gas and oil (2010-2023)")
    plt.suptitle("")
    plt.ylabel(value_label)
    plt.show()

def plot_fig8(global_product_df, value_label):
    df = global_product_df[global_product_df["Product"] == "Coal"]
    df.boxplot(column="Value (B USD)", by="Product")
    plt.xticks(rotation=90)
    plt.title("Figure 8: Global subsidies for coal (2010-2023)")
    plt.suptitle("")
    plt.ylabel(value_label)
    plt.show()

def plot_fig9(country_product_df, value_label):
    n = 8
    country_product_df[country_product_df["Product"] == "Coal"]["Value (B USD)"].describe()
    for prod in country_product_df["Product"].unique():
        if prod != "Coal":
            n += 1
            df = country_product_df[country_product_df["Product"] == prod]
            max_val = df["Value (B USD)"].max()
            df.boxplot(column="Value (B USD)", by="Year", showfliers=False)
            plt.xticks(rotation=90)
            plt.title(f"Figure {n}: Global subsidies for {prod.lower()}")
            plt.suptitle("")
            plt.xlabel("Year")
            plt.ylabel(value_label)
            plt.show()

def plot_fig12(global_product_df):
    df_sorted = global_product_df.sort_values(["Product", "Year"])
    df_sorted["% change"] = df_sorted.groupby("Product")["Value (B USD)"].pct_change() * 100
    plt.figure(figsize=(12, 6))
    for prod in df_sorted["Product"].unique():
        plot_df = df_sorted[df_sorted["Product"] == prod]
        plt.plot(plot_df["Year"], plot_df["% change"], label=prod)
    plt.xlabel("Year")
    plt.ylabel("% change")
    plt.title("Figure 12: Year-over-year % change in subsidies")
    plt.grid()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()

def plot_fig13(country_product_df):
    data = country_product_df.groupby("Country", as_index=False)["Value (B USD)"].sum()
    fig = px.choropleth(
        data,
        locations="Country",
        locationmode="country names",
        color="Value (B USD)",
        color_continuous_scale="Reds",
        hover_name="Country",
        title="Figure 13: Total fossil fuel and electricity subsidies by country"
    )
    fig.update_layout(geo=dict(showframe=False, showcoastlines=False, projection_type='equirectangular'))
    fig.show()

def plot_fig14(country_elec_df, country_fossil_df, country_total_df, value_label="Value (Real 2023 USD, billions)"):
    country_fossil_agg_df = country_fossil_df.groupby(["Country", "Year"])["Value (B USD)"].sum().reset_index()
    country_fossil_agg_df["Product"] = "Fossil fuels"

    top5 = country_total_df.groupby("Year").apply(lambda x: x.nlargest(5, "Value (B USD)")).reset_index(drop=True)
    df_combined = pd.concat([country_elec_df, country_fossil_agg_df], axis=0, ignore_index=True)
    df_top5 = df_combined.merge(top5[["Country", "Year"]], on=["Country", "Year"], how="inner")

    df_pivot = df_top5.pivot_table(index=["Country", "Year"], columns="Product", values="Value (B USD)", fill_value=0).reset_index()
    years = sorted(df_pivot["Year"].unique())
    bar_width = 0.25
    gap = 0.05
    group_gap = 0.5
    colors = {"Fossil fuels": "#1f77b4", "Electricity": "#ff7f0e"}

    positions = []
    group_positions = []
    current_pos = 0
    for year in years:
        df_year = df_pivot[df_pivot["Year"] == year]
        for i in range(len(df_year)):
            positions.append(current_pos + i * (bar_width + gap))
        group_positions.append(current_pos + (len(df_year) * (bar_width + gap) - gap) / 2)
        current_pos += len(df_year) * (bar_width + gap) + group_gap

    median_by_year = country_total_df.groupby("Year")["Value (B USD)"].median()

    fig, ax = plt.subplots(figsize=(16, 8))
    max_height = 0
    for idx, row in df_pivot.iterrows():
        year_idx = years.index(row["Year"])
        df_year = df_pivot[df_pivot["Year"] == row["Year"]]
        bar_pos = positions[sum(len(df_pivot[df_pivot["Year"] == y]) for y in years[:year_idx]) + list(df_year.index).index(idx)]

        bottom = row["Fossil fuels"]
        ax.bar(bar_pos, row["Fossil fuels"], bar_width, color=colors["Fossil fuels"], label="Fossil fuels" if idx == 0 else "")
        ax.bar(bar_pos, row["Electricity"], bar_width, bottom=row["Fossil fuels"], color=colors["Electricity"], label="Electricity" if idx == 0 else "")

        total_height = row["Fossil fuels"] + row["Electricity"]
        ax.text(bar_pos, total_height + 1, row["Country"], ha="center", va="bottom", fontsize=9, rotation=90, color="black")

        max_height = max(max_height, total_height)

    median_values = [median_by_year[year] for year in years]
    ax.plot(group_positions, median_values, color='red', markersize=10, label='Median global subsidy')

    ax.set_xticks(group_positions)
    ax.set_xticklabels(years)
    ax.set_ylabel(value_label)
    ax.set_title("Figure 14: Top 5 countries based on total subsidies each year")
    ax.set_ylim(0, max_height * 1.15)
    ax.legend()
    plt.tight_layout()
    plt.show()
