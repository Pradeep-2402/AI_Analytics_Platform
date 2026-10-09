def generate_dataset_summary(df):

    summary = ""

    # Revenue Analysis
    if "Total_Sales" in df.columns:

        summary += f"""
BUSINESS METRICS

Total Revenue:
{df['Total_Sales'].sum():,.2f}

Average Revenue:
{df['Total_Sales'].mean():,.2f}

Highest Revenue:
{df['Total_Sales'].max():,.2f}
"""

    # Product Analysis
    if "Product" in df.columns:

        summary += f"""

Top Products:
{df['Product'].value_counts().head(5).to_string()}
"""

    # City Analysis
    if "City" in df.columns:

        summary += f"""

Top Cities:
{df['City'].value_counts().head(5).to_string()}
"""

    # Category Analysis
    if "Category" in df.columns:

        summary += f"""

Top Categories:
{df['Category'].value_counts().head(5).to_string()}
"""

    # Data Quality LAST
    summary += f"""

DATA QUALITY

Rows: {len(df)}
Columns: {len(df.columns)}
Duplicates: {int(df.duplicated().sum())}
Null Values: {int(df.isnull().sum().sum())}

Column Names:
{list(df.columns)}
"""

    return summary