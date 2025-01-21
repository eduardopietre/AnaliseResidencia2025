import os
import pandas as pd

from checkhash import print_file_hash


def generate_excel_by_specialty(df, output_file):
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for i, specialty in enumerate(sorted(df['ESPECIALIDADE'].unique())):
            filtered_df = df[df['ESPECIALIDADE'] == specialty]
            filtered_df = filtered_df.sort_values(by="FINAL", ascending=False)
            filtered_df = filtered_df.reset_index(drop=True)
            filtered_df.insert(0, "N", 0)
            filtered_df["N"] = filtered_df.index + 1

            sheet_name = specialty.replace("ACESSO DIRETO - ", "").replace("MEDICINA DE ", "")
            sheet_name = sheet_name.replace("MEDICINA ", "").replace("CLÍNICA/LABORATORI", "CLÍNICA")
            sheet_name = str(i) + " " + sheet_name
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]

            print("Salvando aba:", sheet_name)
            filtered_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Ajusta as dimensões das colunas e aplica centralização
            worksheet = writer.sheets[sheet_name]
            center_format = writer.book.add_format({'align': 'center'})

            for col_num, value in enumerate(filtered_df.columns):
                max_length = max(
                    filtered_df[value].astype(str).map(len).max(),  # Comprimento máximo dos dados
                    len(value)  # Comprimento do cabeçalho
                ) + 8  # Adiciona margem para legibilidade

                # Centraliza se necessário
                if col_num in [0, 2, 3, 4, 5]:
                    worksheet.set_column(col_num, col_num, max_length, center_format)
                else:
                    worksheet.set_column(col_num, col_num, max_length)


def merge(file_notas: str):
    df = pd.read_csv(file_notas)

    print_file_hash(os.getcwd(), file_notas)
    print(f"Processando notas finais em {file_notas}... Por favor aguarde.")

    df.sort_values(by="FINAL", ascending=False, inplace=True)

    out_file = "notas_pareadas_por_especialidades.xlsx"
    generate_excel_by_specialty(df, out_file)
    print_file_hash(os.getcwd(), out_file)
    print(f"Notas pareadas por especialidade exportadas para '{out_file}'.")


def main():
    file_notas = "nota-final-enare-residencia-medica.csv"
    merge(file_notas)


if __name__ == '__main__':
    main()
