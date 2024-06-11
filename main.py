import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import xml.sax.saxutils as saxutils


def extract_text_from_pdf(pdf_file):
    pdf_bytes = pdf_file.read()
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""

    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        if not image_list:
            continue
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            page_text = pytesseract.image_to_string(image)
            text += page_text 
            # + "\n"

    return text


def create_pdf_with_text(text, output_pdf_path):
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        name='Justify',
        parent=styles['Normal'],
        alignment=4,
        leading=12,
        spaceAfter=6,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=0
    )

    sanitized_text = saxutils.escape(text)
    paragraphs = sanitized_text.split('\n')
    flowables = []
    for para in paragraphs:
        if para.strip():
            p = Paragraph(para, style)
            flowables.append(p)
            flowables.append(Spacer(1, 0.1 * inch))
    doc.build(flowables)


st.title("PDF Text Extraction and Generation")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    extracted_text = extract_text_from_pdf(uploaded_file)
    st.subheader("Extracted Text")
    st.text(extracted_text)
    if st.button("Generate PDF with Extracted Text"):
        output_pdf_path = "extracted_text.pdf"
        create_pdf_with_text(extracted_text, output_pdf_path)
        with open(output_pdf_path, "rb") as file:
            btn = st.download_button(
                label="Download PDF",
                data=file,
                file_name="extracted_text.pdf",
                mime="application/pdf"
            )
