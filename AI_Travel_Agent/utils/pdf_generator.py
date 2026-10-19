import re
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet


def _rs(amount):
    # The default PDF fonts have no rupee glyph, so use "Rs."
    return f"Rs. {amount:,}"


def _markdown_to_rl(text):
    """Very small markdown -> reportlab markup converter."""

    lines = []

    for line in text.split("\n"):
        line = escape(line)
        line = re.sub(r"^#{1,6}\s*(.+)$", r"<b>\1</b>", line)
        line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
        line = re.sub(r"^\s*[\*\-]\s+", "• ", line)
        lines.append(line)

    return "<br/>".join(lines)


def generate_pdf(
    destination,
    days,
    budget,
    best_hotel,
    itinerary,
    travel=None,
    origin="",
    travel_date=None
):
    """Build the PDF in memory and return its bytes."""

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            f"<b>AI Travel Guide - {escape(destination)}</b>",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 12))

    if origin:
        content.append(
            Paragraph(
                f"<b>From:</b> {escape(origin)}",
                styles["Normal"]
            )
        )

    if travel_date:
        content.append(
            Paragraph(
                f"<b>Travel Date:</b> {travel_date}",
                styles["Normal"]
            )
        )

    content.append(
        Paragraph(
            f"<b>Duration:</b> {days} Days",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>User Budget:</b> {_rs(budget['user_budget'])}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Estimated Cost:</b> {_rs(budget['estimated_total'])}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 12))

    # ---------------- TRAVEL (train / flight / bus) ----------------

    if travel:

        for mode, options in travel.items():

            if not options:
                continue

            content.append(
                Paragraph(
                    f"<b>{escape(mode.title())} Options</b> "
                    f"(approximate - verify before booking)",
                    styles["Heading2"]
                )
            )

            for t in options:

                content.append(
                    Paragraph(
                        f"{escape(t['number'])} "
                        f"{escape(t['name'])}: "
                        f"{escape(t['from_station'])} {t['departure']} -> "
                        f"{escape(t['to_station'])} {t['arrival']} "
                        f"({escape(t['duration'])}) - "
                        f"from {_rs(t['fare']) if t['fare'] else 'N/A'}"
                        + (" per vehicle" if t.get("per_vehicle") else " per person"),
                        styles["Normal"]
                    )
                )

            content.append(Spacer(1, 12))

    # ---------------- HOTEL ----------------

    content.append(
        Paragraph(
            "<b>Best Hotel Recommendation</b>",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            escape(best_hotel["name"]),
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Cost Per Night: {_rs(best_hotel['price_per_night'])}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(
            "<b>Hotel Highlights</b>",
            styles["Heading3"]
        )
    )

    for item in best_hotel["highlights"]:

        content.append(
            Paragraph(
                f"• {escape(item)}",
                styles["Normal"]
            )
        )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(
            "<b>Travel Itinerary</b>",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            _markdown_to_rl(itinerary),
            styles["Normal"]
        )
    )

    doc.build(content)

    return buffer.getvalue()