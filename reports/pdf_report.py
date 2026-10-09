import os
import io
import math
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, KeepTogether, PageBreak
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable


# ── Colour Palette ──────────────────────────────────────────────────────────
C_BG         = colors.HexColor("#0a0e1a")
C_CARD       = colors.HexColor("#0f1629")
C_CARD2      = colors.HexColor("#131c35")
C_CYAN       = colors.HexColor("#00d4ff")
C_CYAN_DIM   = colors.HexColor("#00a8cc")
C_PURPLE     = colors.HexColor("#7c3aed")
C_GREEN      = colors.HexColor("#10b981")
C_AMBER      = colors.HexColor("#f59e0b")
C_RED        = colors.HexColor("#ef4444")
C_TEXT       = colors.HexColor("#e2e8f0")
C_MUTED      = colors.HexColor("#64748b")
C_DIM        = colors.HexColor("#94a3b8")
C_YELLOW     = colors.HexColor("#fde047")
C_WHITE      = colors.white
C_BLACK      = colors.black


# ── Custom Flowables ─────────────────────────────────────────────────────────
class ColorRect(Flowable):
    """A filled rectangle used as a section divider / accent bar."""
    def __init__(self, width, height, fill_color):
        Flowable.__init__(self)
        self.width  = width
        self.height = height
        self.fill   = fill_color

    def draw(self):
        self.canv.setFillColor(self.fill)
        self.canv.rect(0, 0, self.width, self.height, stroke=0, fill=1)


class GradientHeader(Flowable):
    """Full-width dark header band with title text."""
    def __init__(self, width, title, subtitle=""):
        Flowable.__init__(self)
        self.width    = width
        self.height   = 110
        self.title    = title
        self.subtitle = subtitle

    def draw(self):
        c = self.canv
        # dark background
        c.setFillColor(C_BG)
        c.rect(0, 0, self.width, self.height, stroke=0, fill=1)
        # cyan accent bar top
        c.setFillColor(C_CYAN)
        c.rect(0, self.height - 4, self.width, 4, stroke=0, fill=1)
        # purple accent bar bottom
        c.setFillColor(C_PURPLE)
        c.rect(0, 0, self.width, 3, stroke=0, fill=1)
        # title
        c.setFillColor(C_CYAN)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(24, self.height - 38, self.title)
        # subtitle
        c.setFillColor(C_DIM)
        c.setFont("Helvetica", 10)
        c.drawString(24, self.height - 56, self.subtitle)
        # decorative dots
        for i, col in enumerate([C_CYAN, C_PURPLE, C_GREEN]):
            c.setFillColor(col)
            c.circle(self.width - 30 - i * 18, self.height - 28, 6, stroke=0, fill=1)


class SectionHeader(Flowable):
    """Cyan left-bar section heading."""
    def __init__(self, width, text, icon=""):
        Flowable.__init__(self)
        self.width  = width
        self.height = 36
        self.text   = text
        self.icon   = icon

    def draw(self):
        c = self.canv
        # card background
        c.setFillColor(C_CARD)
        c.roundRect(0, 0, self.width, self.height, 6, stroke=0, fill=1)
        # cyan left bar
        c.setFillColor(C_CYAN)
        c.rect(0, 0, 5, self.height, stroke=0, fill=1)
        # text
        c.setFillColor(C_CYAN)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(18, 11, f"{self.icon}  {self.text}" if self.icon else self.text)


class KPIRow(Flowable):
    """A row of KPI metric cards."""
    def __init__(self, width, metrics):
        """metrics: list of (label, value, color) tuples"""
        Flowable.__init__(self)
        self.width   = width
        self.metrics = metrics
        n = len(metrics)
        self.height  = 70
        self.card_w  = (width - (n - 1) * 10) / n

    def draw(self):
        c   = self.canv
        n   = len(self.metrics)
        cw  = (self.width - (n - 1) * 10) / n
        for i, (label, value, col) in enumerate(self.metrics):
            x = i * (cw + 10)
            # card bg
            c.setFillColor(C_CARD)
            c.roundRect(x, 0, cw, self.height, 8, stroke=0, fill=1)
            # top accent
            c.setFillColor(col)
            c.rect(x, self.height - 3, cw, 3, stroke=0, fill=1)
            # border
            c.setStrokeColor(C_MUTED)
            c.setLineWidth(0.5)
            c.roundRect(x, 0, cw, self.height, 8, stroke=1, fill=0)
            # value
            c.setFillColor(col)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(x + cw / 2, self.height - 32, str(value))
            # label
            c.setFillColor(C_DIM)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x + cw / 2, 12, label.upper())


# ── Matplotlib chart helpers ─────────────────────────────────────────────────
MPL_DARK = {
    "figure.facecolor":  "#0a0e1a",
    "axes.facecolor":    "#0f1629",
    "axes.edgecolor":    "#1e2d50",
    "axes.labelcolor":   "#94a3b8",
    "xtick.color":       "#64748b",
    "ytick.color":       "#64748b",
    "text.color":        "#e2e8f0",
    "grid.color":        "#1e2d50",
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
}


def _fig_to_image(fig, width_cm=17, height_cm=8):
    """Render a matplotlib figure to a ReportLab Image flowable."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return Image(buf, width=width_cm * cm, height=height_cm * cm)


def make_null_bar_chart(column_profile_df):
    """Bar chart: null values per column."""
    if True:
        fig, ax = plt.subplots(figsize=(11, 4))
        fig.patch.set_facecolor("#0a0e1a")
        ax.set_facecolor("#0f1629")

        cols   = column_profile_df["column"].tolist()
        nulls  = column_profile_df["null_count"].tolist()
        bar_colors = ["#00d4ff" if n == 0 else "#ef4444" if n > 50 else "#f59e0b"
                      for n in nulls]

        bars = ax.bar(cols, nulls, color=bar_colors, edgecolor="#1e2d50", linewidth=0.8)
        ax.set_title("Null Values by Column", color="#00d4ff", fontsize=13, pad=12, fontweight="bold")
        ax.set_xlabel("Column", color="#94a3b8", fontsize=9)
        ax.set_ylabel("Null Count", color="#94a3b8", fontsize=9)
        ax.tick_params(axis="x", rotation=45, labelsize=7, colors="#64748b")
        ax.tick_params(axis="y", labelsize=7, colors="#64748b")
        ax.grid(axis="y", alpha=0.3, color="#1e2d50", linestyle="--")
        for spine in ax.spines.values():
            spine.set_edgecolor("#1e2d50")
        # value labels
        for bar, val in zip(bars, nulls):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                        str(val), ha="center", va="bottom", color="#e2e8f0", fontsize=7)
        fig.tight_layout()
        return fig


def make_quality_pie(valid, invalid):
    """Donut chart: valid vs invalid records."""
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor("#0a0e1a")
    ax.set_facecolor("#0a0e1a")
    sizes  = [valid, invalid]
    clrs   = ["#10b981", "#ef4444"]
    labels = [f"Valid\n{valid}", f"Invalid\n{invalid}"]
    wedges, texts = ax.pie(
        sizes, colors=clrs, startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="#0a0e1a", linewidth=2)
    )
    ax.legend(wedges, labels, loc="lower center", frameon=False,
              labelcolor="#e2e8f0", fontsize=9, ncol=2)
    ax.set_title("Record Quality", color="#00d4ff", fontsize=12, fontweight="bold", pad=10)
    fig.tight_layout()
    return fig


def make_forecast_chart(forecast_df, metric_name="Value"):
    """Line chart: forecast yhat with confidence band."""
    fig, ax = plt.subplots(figsize=(11, 4))
    fig.patch.set_facecolor("#0a0e1a")
    ax.set_facecolor("#0f1629")

    ds   = pd.to_datetime(forecast_df["ds"])
    yhat = forecast_df["yhat"]
    ylo  = forecast_df["yhat_lower"]
    yhi  = forecast_df["yhat_upper"]

    ax.plot(ds, yhat, color="#00d4ff", linewidth=2, label="Forecast")
    ax.fill_between(ds, ylo, yhi, color="#00d4ff", alpha=0.15, label="Confidence Band")
    ax.set_title(f"{metric_name} — Forecast Trend", color="#00d4ff",
                 fontsize=13, pad=12, fontweight="bold")
    ax.set_xlabel("Date", color="#94a3b8", fontsize=9)
    ax.set_ylabel(metric_name, color="#94a3b8", fontsize=9)
    ax.tick_params(axis="x", rotation=30, labelsize=7, colors="#64748b")
    ax.tick_params(axis="y", labelsize=7, colors="#64748b")
    ax.grid(alpha=0.3, color="#1e2d50", linestyle="--")
    ax.legend(frameon=False, labelcolor="#e2e8f0", fontsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#1e2d50")
    fig.tight_layout()
    return fig


def make_anomaly_chart(anomalies, health_score):
    """Horizontal bar + gauge-style health score."""
    fig = plt.figure(figsize=(11, max(3, len(anomalies) * 0.55 + 2)))
    fig.patch.set_facecolor("#0a0e1a")

    gs = fig.add_gridspec(1, 3, wspace=0.4)
    ax_list  = fig.add_subplot(gs[0, :2])
    ax_gauge = fig.add_subplot(gs[0, 2])

    # anomaly list bars
    ax_list.set_facecolor("#0f1629")
    if anomalies:
        y_pos  = range(len(anomalies))
        labels = [a[:55] + "…" if len(a) > 55 else a for a in anomalies]
        cols   = ["#ef4444" if "High" in a or "Outlier" in a or "Missing" in a
                  else "#f59e0b" for a in anomalies]
        ax_list.barh(list(y_pos), [1] * len(anomalies), color=cols,
                     edgecolor="#1e2d50", linewidth=0.5, height=0.6)
        ax_list.set_yticks(list(y_pos))
        ax_list.set_yticklabels(labels, fontsize=7, color="#e2e8f0")
        ax_list.set_xticks([])
        ax_list.set_title("Detected Anomalies", color="#00d4ff", fontsize=11,
                          fontweight="bold", pad=8)
    else:
        ax_list.text(0.5, 0.5, "✓  No Anomalies Detected",
                     ha="center", va="center", color="#10b981",
                     fontsize=13, fontweight="bold", transform=ax_list.transAxes)
        ax_list.set_title("Anomaly Detection", color="#00d4ff", fontsize=11,
                          fontweight="bold", pad=8)
    for spine in ax_list.spines.values():
        spine.set_edgecolor("#1e2d50")

    # health score gauge
    ax_gauge.set_facecolor("#0a0e1a")
    ax_gauge.set_xlim(-1.3, 1.3)
    ax_gauge.set_ylim(-0.2, 1.3)
    ax_gauge.set_aspect("equal")
    ax_gauge.axis("off")
    theta_bg = [math.pi * (1 - i / 100) for i in range(101)]
    for i in range(100):
        t1, t2 = theta_bg[i], theta_bg[i + 1]
        col = "#10b981" if i >= 70 else "#f59e0b" if i >= 40 else "#ef4444"
        ax_gauge.plot([math.cos(t1), math.cos(t2)],
                      [math.sin(t1), math.sin(t2)],
                      color=col, linewidth=8, alpha=0.25)
    angle = math.pi * (1 - health_score / 100)
    ax_gauge.annotate("", xy=(0.75 * math.cos(angle), 0.75 * math.sin(angle)),
                      xytext=(0, 0),
                      arrowprops=dict(arrowstyle="->", color="#00d4ff", lw=2.5))
    score_col = "#10b981" if health_score >= 70 else "#f59e0b" if health_score >= 40 else "#ef4444"
    ax_gauge.text(0, 0.25, f"{int(health_score)}", ha="center", va="center",
                  color=score_col, fontsize=22, fontweight="bold")
    ax_gauge.text(0, 0.05, "Health Score", ha="center", va="center",
                  color="#94a3b8", fontsize=8)
    fig.tight_layout()
    return fig


# ── Tiny RC context helper ────────────────────────────────────────────────────
class MPLRC:
    """Context manager that does nothing — we set facecolors manually."""
    def __enter__(self): return self
    def __exit__(self, *a): pass


# ── Style helpers ─────────────────────────────────────────────────────────────
def _styles():
    base = getSampleStyleSheet()
    custom = {
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"],
            fontSize=26, textColor=C_CYAN, spaceAfter=6,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=base["Normal"],
            fontSize=11, textColor=C_DIM, spaceAfter=4,
            alignment=TA_CENTER,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontSize=9, textColor=C_TEXT, leading=14,
            spaceAfter=4,
        ),
        "body_muted": ParagraphStyle(
            "body_muted", parent=base["Normal"],
            fontSize=8, textColor=C_DIM, leading=12,
            spaceAfter=2,
        ),
        "insight_line": ParagraphStyle(
            "insight_line", parent=base["Normal"],
            fontSize=9, textColor=C_TEXT, leading=15,
            leftIndent=10, spaceAfter=3,
        ),
        "anomaly_item": ParagraphStyle(
            "anomaly_item", parent=base["Normal"],
            fontSize=8.5, textColor=C_AMBER, leading=14,
            leftIndent=12, spaceAfter=2,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"],
            fontSize=7, textColor=C_MUTED,
            alignment=TA_CENTER,
        ),
    }
    return base, custom


def _dark_table(data, col_widths=None, header_bg=C_CARD2, header_fg=C_CYAN,
                row_bg=C_CARD, alt_bg=C_CARD2, accent=C_CYAN):
    """Build a consistently styled dark table."""
    n_rows = len(data)
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        # Header
        ("BACKGROUND",  (0, 0), (-1, 0),      header_bg),
        ("TEXTCOLOR",   (0, 0), (-1, 0),      header_fg),
        ("FONTNAME",    (0, 0), (-1, 0),      "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),      9),
        ("ALIGN",       (0, 0), (-1, 0),      "CENTER"),
        ("TOPPADDING",  (0, 0), (-1, 0),      8),
        ("BOTTOMPADDING", (0, 0), (-1, 0),    8),
        ("LINEBELOW",   (0, 0), (-1, 0),      1.5, accent),
        # Body rows
        ("FONTNAME",    (0, 1), (-1, -1),     "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1),     8.5),
        ("TEXTCOLOR",   (0, 1), (-1, -1),     C_WHITE),
        ("ALIGN",       (0, 1), (-1, -1),     "CENTER"),
        ("TOPPADDING",  (0, 1), (-1, -1),     6),
        ("BOTTOMPADDING", (0, 1), (-1, -1),   6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),  [row_bg, alt_bg]),
        # Grid
        ("GRID",        (0, 0), (-1, -1),     0.4, C_MUTED),
        ("BOX",         (0, 0), (-1, -1),     1,   accent),
        ("ROUNDEDCORNERS", [6]),
    ]
    tbl.setStyle(TableStyle(style))
    return tbl


# ── Canvas background callback ────────────────────────────────────────────────
def _page_background(canvas_obj, doc):
    """Paint dark background on every page."""
    canvas_obj.saveState()
    canvas_obj.setFillColor(C_BG)
    canvas_obj.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    # subtle top gradient strip
    canvas_obj.setFillColor(C_CARD)
    canvas_obj.rect(0, A4[1] - 6, A4[0], 6, stroke=0, fill=1)
    # footer line
    canvas_obj.setStrokeColor(C_MUTED)
    canvas_obj.setLineWidth(0.4)
    canvas_obj.line(2 * cm, 1.8 * cm, A4[0] - 2 * cm, 1.8 * cm)
    canvas_obj.setFillColor(C_MUTED)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawCentredString(
        A4[0] / 2, 1.3 * cm,
        "AI-Powered Data Quality & Analytics Platform  |  Confidential"
    )
    canvas_obj.drawRightString(
        A4[0] - 2 * cm, 1.3 * cm,
        f"Page {doc.page}"
    )
    canvas_obj.restoreState()


# ── Main generator ─────────────────────────────────────────────────────────────
def generate_pdf_report(
    profile,
    quality_report,
    ai_insights,
    output_path="outputs/analytics_report.pdf",
    # Optional extras (pass from session_state when available)
    column_profile_df=None,   # pd.DataFrame with 'column','null_count' cols
    forecast_df=None,         # pd.DataFrame with ds,yhat,yhat_lower,yhat_upper
    forecast_metric=None,     # str — name of the forecast metric column
    anomalies=None,           # list[str]
    health_score=None,        # int 0-100
):
    os.makedirs("outputs", exist_ok=True)

    base_styles, S = _styles()
    W = A4[0] - 4 * cm   # usable width

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm,  bottomMargin=2.5 * cm,
    )

    story = []

    # ── COVER / HEADER ────────────────────────────────────────────────────────
    story.append(GradientHeader(
        W,
        title="⚡ AI Analytics Platform Report",
        subtitle="Data Quality  ·  Validation  ·  Forecasting  ·  AI Insights"
    ))
    story.append(Spacer(1, 18))

    # ── DATASET SUMMARY KPIs ──────────────────────────────────────────────────
    story.append(SectionHeader(W, "Dataset Summary", "📊"))
    story.append(Spacer(1, 10))

    story.append(KPIRow(W, [
        ("Total Rows",      profile.get("rows", "—"),           C_CYAN),
        ("Total Columns",   profile.get("columns", "—"),        C_PURPLE),
        ("Duplicate Rows",  profile.get("duplicate_rows", "—"), C_AMBER),
        ("Total Nulls",     profile.get("total_nulls", "—"),    C_RED),
    ]))
    story.append(Spacer(1, 14))

    # summary table
    summary_data = [
        ["Metric", "Value"],
        ["Total Rows",      str(profile.get("rows", "—"))],
        ["Total Columns",   str(profile.get("columns", "—"))],
        ["Duplicate Rows",  str(profile.get("duplicate_rows", "—"))],
        ["Total Nulls",     str(profile.get("total_nulls", "—"))],
    ]
    story.append(_dark_table(summary_data, col_widths=[W * 0.55, W * 0.45],
                             accent=C_CYAN))
    story.append(Spacer(1, 18))

    # ── NULL VALUES CHART ─────────────────────────────────────────────────────
    if column_profile_df is not None and not column_profile_df.empty:
        story.append(SectionHeader(W, "Null Values by Column", "📉"))
        story.append(Spacer(1, 8))
        fig = make_null_bar_chart(column_profile_df)
        story.append(_fig_to_image(fig, width_cm=17, height_cm=7))
        story.append(Spacer(1, 18))

    # ── DATA QUALITY REPORT ───────────────────────────────────────────────────
    story.append(SectionHeader(W, "Data Quality Report", "✅"))
    story.append(Spacer(1, 10))

    # KPI row
    qs = quality_report.get("quality_score", 0) if quality_report else 0
    qs_str = str(qs)
    qs_col = C_GREEN if float(str(qs).replace("%", "") or 0) >= 80 \
        else C_AMBER if float(str(qs).replace("%", "") or 0) >= 50 else C_RED

    valid_n   = quality_report.get("valid_records",   "—") if quality_report else "—"
    invalid_n = quality_report.get("invalid_records", "—") if quality_report else "—"

    story.append(KPIRow(W, [
        ("Valid Records",   valid_n,   C_GREEN),
        ("Invalid Records", invalid_n, C_RED),
        ("Quality Score",   qs_str,    qs_col),
    ]))
    story.append(Spacer(1, 12))

    quality_data = [
        ["Metric", "Value"],
        ["Valid Records",   str(valid_n)],
        ["Invalid Records", str(invalid_n)],
        ["Quality Score",   str(qs_str)],
    ]
    story.append(_dark_table(quality_data, col_widths=[W * 0.55, W * 0.45],
                             header_bg=colors.HexColor("#0d3320"), accent=C_GREEN))
    story.append(Spacer(1, 12))

    # quality donut chart
    try:
        v = int(str(valid_n))
        iv = int(str(invalid_n))
        if v + iv > 0:
            fig = make_quality_pie(v, iv)
            story.append(_fig_to_image(fig, width_cm=9, height_cm=9))
    except Exception:
        pass
    story.append(Spacer(1, 18))

    # ── FORECAST ──────────────────────────────────────────────────────────────
    if forecast_df is not None and not forecast_df.empty:
        story.append(PageBreak())
        story.append(SectionHeader(W, "Forecast Analysis", "📈"))
        story.append(Spacer(1, 8))

        metric = forecast_metric or "Value"
        fig = make_forecast_chart(forecast_df, metric)
        story.append(_fig_to_image(fig, width_cm=17, height_cm=7))
        story.append(Spacer(1, 10))

        # forecast table — last 20 rows
        tail = forecast_df[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(20).copy()
        tail["ds"]         = pd.to_datetime(tail["ds"]).dt.strftime("%Y-%m-%d")
        tail["yhat"]       = tail["yhat"].round(2)
        tail["yhat_lower"] = tail["yhat_lower"].round(2)
        tail["yhat_upper"] = tail["yhat_upper"].round(2)

        fcast_data = [["Date", "Forecast", "Lower Bound", "Upper Bound"]]
        for _, row in tail.iterrows():
            fcast_data.append([
                str(row["ds"]), str(row["yhat"]),
                str(row["yhat_lower"]), str(row["yhat_upper"])
            ])
        story.append(_dark_table(fcast_data,
                                 col_widths=[W*0.28, W*0.24, W*0.24, W*0.24],
                                 header_bg=colors.HexColor("#0d1f3c"), accent=C_CYAN))
        story.append(Spacer(1, 18))

    # ── ANOMALY DETECTION ─────────────────────────────────────────────────────
    if anomalies is not None:
        story.append(SectionHeader(W, "Anomaly Detection", "🚨"))
        story.append(Spacer(1, 8))

        if health_score is not None:
            fig = make_anomaly_chart(anomalies, health_score)
            story.append(_fig_to_image(fig, width_cm=17, height_cm=max(4, len(anomalies) * 0.55 + 2)))
            story.append(Spacer(1, 10))

        if anomalies:
            anom_data = [["#", "Anomaly Description"]]
            for idx, a in enumerate(anomalies, 1):
                anom_data.append([str(idx), a])
            story.append(_dark_table(anom_data,
                                     col_widths=[W * 0.08, W * 0.92],
                                     header_bg=colors.HexColor("#3b0f0f"), accent=C_RED))
        else:
            story.append(Paragraph("✓  No anomalies were detected in this dataset.",
                                   S["body"]))
        story.append(Spacer(1, 18))

    # ── AI INSIGHTS ───────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(SectionHeader(W, "AI-Generated Insights", "🧠"))
    story.append(Spacer(1, 10))

    if ai_insights and ai_insights.strip() and ai_insights != "AI insights not generated yet.":
        lines = ai_insights.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 4))
                continue
            # detect markdown-style bullets / headers
            if line.startswith("##"):
                txt = line.lstrip("#").strip()
                story.append(Spacer(1, 6))
                story.append(ColorRect(W, 1.5, C_CYAN))
                story.append(Spacer(1, 4))
                p = Paragraph(txt, ParagraphStyle(
                    "insight_h", fontSize=11, textColor=C_CYAN,
                    fontName="Helvetica-Bold", spaceAfter=4
                ))
                story.append(p)
            elif line.startswith("#"):
                txt = line.lstrip("#").strip()
                p = Paragraph(txt, ParagraphStyle(
                    "insight_h2", fontSize=10, textColor=C_PURPLE,
                    fontName="Helvetica-Bold", spaceAfter=4
                ))
                story.append(p)
            elif line.startswith(("- ", "* ", "• ")):
                txt = "•  " + line[2:].strip()
                story.append(Paragraph(txt, S["insight_line"]))
            elif line.startswith(tuple("123456789")):
                story.append(Paragraph(line, S["insight_line"]))
            else:
                story.append(Paragraph(line, S["body"]))
    else:
        story.append(Paragraph(
            "AI insights have not been generated yet. "
            "Navigate to the AI Insights page and click 'Generate AI Insights' "
            "before exporting this report.",
            S["body_muted"]
        ))

    story.append(Spacer(1, 24))

    # ── FOOTER STAMP ──────────────────────────────────────────────────────────
    story.append(HRFlowable(width=W, color=C_MUTED, thickness=0.5))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Report Generated by AI Analytics Platform  |  "
        "Built with Streamlit · PySpark · MySQL · Prophet · Ollama",
        S["footer"]
    ))

    # ── BUILD ─────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=_page_background, onLaterPages=_page_background)
    return output_path