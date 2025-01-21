import pandas as pd
from fpdf import FPDF, XPos, YPos
import os


def excel_to_pdf(excel_file, output_pdf):
    excel_data = pd.read_excel(excel_file, sheet_name=None)

    pdf = FPDF(orientation="P", unit="mm", format="A3")
    pdf.set_auto_page_break(auto=True, margin=5)

    for sheet_name, data in excel_data.items():
        # Divide o DataFrame em chunks para evitar quebra na página
        rows_per_page = 40
        chunks = [data.iloc[i:i + rows_per_page] for i in range(0, len(data), rows_per_page)]

        col_widths = []
        for i, col in enumerate(data.columns):
            max_content_length = max(
                data[col].astype(str).apply(len).max(),
                len(col)
            )
            if i == 5:
                max_content_length = min(max_content_length, 27 + 3)
            col_width = (max_content_length * 1.4) + 7  # Ajuste fino necessário para evitar overflow
            col_widths.append(col_width)

        for i, chunk in enumerate(chunks):
            pdf.add_page()

            pdf.set_font("Helvetica", style='B', size=14)
            title = f"{sheet_name} (continuação)" if i > 0 else sheet_name
            pdf.cell(0, 5, text=title.encode('latin-1', 'replace').decode('latin-1'), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

            # Escreve o cabeçalho da tabela
            pdf.set_font("Helvetica", size=8)
            pdf.ln(3)  # Espaçamento
            header = chunk.columns.tolist()

            for idx, col in enumerate(header):
                pdf.cell(col_widths[idx], 6, text=col.encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
            pdf.ln()

            # Escreve os dados
            rows = chunk.values.tolist()
            for row in rows:
                for idx, item in enumerate(row):
                    if idx == 7:
                        item = item.replace("ACESSO DIRETO - ", "").replace("MEDICINA DE ", "")
                        item = item.replace("MEDICINA ", "").replace("CLÍNICA/LABORATORI", "CLÍNICA")

                        if len(item) > 27:
                            item = item[:27] + "..."

                    cell_value = str(item).encode('latin-1', 'replace').decode('latin-1')
                    pdf.cell(col_widths[idx], 6, text=cell_value, border=1, align='C')
                pdf.ln()

    pdf.output(output_pdf)


if __name__ == "__main__":
    input_file = "notas_pareadas_por_especialidades.xlsx"
    output_file = "ranking_extraoficial_como_pdf.pdf"

    if os.path.exists(input_file):
        excel_to_pdf(input_file, output_file)
        print(f"PDF gerado com sucesso: {output_file}")
    else:
        print(f"Arquivo Excel não encontrado: {input_file}")
