from fpdf import FPDF

def generate_report(metrics, filename="liquidity_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, text="Liquidity Report", ln=True)

    for k, v in metrics.items():
        pdf.cell(200, 10, text=f"{k}: {v}", ln=True)

    pdf.output(filename)
    return filename
