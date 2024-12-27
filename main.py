from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from io import BytesIO
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def add_watermark(input_pdf, watermark_text="krispnotes.in"):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Create the watermark PDF in memory
    watermark_pdf = BytesIO()
    c = canvas.Canvas(watermark_pdf, pagesize=letter)
    c.setFont("Helvetica-Bold", 36)

    # Set low-opacity watermark color
    c.setFillColor(Color(0.5, 0.5, 0.5,
                         alpha=0.1))  # Gray color with low opacity
    c.saveState()
    c.translate(letter[0] / 2, letter[1] / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, watermark_text)
    c.restoreState()
    c.save()
    watermark_pdf.seek(0)
    watermark_reader = PdfReader(watermark_pdf)

    # Process each page
    for page in reader.pages:
        # Remove the last line (e.g., bottom watermark)
        media_box = page.mediabox
        page.cropbox.lower_left = (media_box.lower_left[0],
                                   media_box.lower_left[1] + 20)

        # Add watermark
        page.merge_page(watermark_reader.pages[0])
        writer.add_page(page)

    # Save the watermarked PDF
    output_pdf = os.path.join(OUTPUT_FOLDER, "output.pdf")
    with open(output_pdf, "wb") as f:
        writer.write(f)

    return output_pdf


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if the file is present in the request
        if "file" not in request.files:
            return "No file part", 400
        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400

        # Save the uploaded file
        input_pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_pdf_path)

        # Add watermark
        output_pdf_path = add_watermark(input_pdf_path)

        return send_file(output_pdf_path, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
