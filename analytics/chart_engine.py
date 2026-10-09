import plotly.express as px

def create_chart(df, chart_type, x_axis=None, y_axis=None):

    if chart_type == "Bar Chart":
        return px.bar(df, x=x_axis, y=y_axis)

    if chart_type == "Line Chart":
        return px.line(df, x=x_axis, y=y_axis)

    if chart_type == "Pie Chart":
        return px.pie(df, names=x_axis, values=y_axis)

    if chart_type == "Scatter Plot":
        return px.scatter(df, x=x_axis, y=y_axis)

    if chart_type == "Histogram":
        return px.histogram(df, x=x_axis)

    if chart_type == "Box Plot":
        return px.box(df, y=y_axis)

    return None


def create_top_n_chart(df, category_column, value_column, n=10):

    grouped_df = (
        df.groupby(category_column)[value_column]
        .sum()
        .reset_index()
        .sort_values(by=value_column, ascending=False)
        .head(n)
    )

    fig = px.bar(
        grouped_df,
        x=category_column,
        y=value_column,
        title=f"Top {n} {category_column} by {value_column}"
    )

    return fig


def create_correlation_heatmap(df):

    numeric_df = df.select_dtypes(include=["int64", "float64"])

    if numeric_df.empty:
        return None

    corr = numeric_df.corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        title="Correlation Heatmap"
    )

    return fig