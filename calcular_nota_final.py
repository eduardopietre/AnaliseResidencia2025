import os
import pandas as pd

from checkhash import print_file_hash


def combine(df_curr, df_notas):
    # Combinar os DataFrames com base na coluna 'INSCRIÇÃO'
    combined_df = pd.merge(df_curr, df_notas, left_on="INSCRIÇÃO", right_on="Inscrição", how="outer", indicator=True)

    # Contar quantas inscrições não foram encontradas
    not_matched_df = combined_df[combined_df["_merge"] != "both"]

    if not_matched_df.shape[0] == 0:
        print(f"Nenhuma linha com pareamento incompleto.")
    else:
        print(f"{not_matched_df.shape[0]} linhas com pareamento incompleto.")
        not_matched_df.to_csv("pareamento_incompleto.csv", index=False)
        print("Linhas com pareamento incompleto exportadas para 'pareamento_incompleto.csv'")

    # Filtra apenas as linhas que parearam
    matched_df = combined_df[combined_df["_merge"] == "both"].drop(columns=["_merge", "Inscrição"])

    # Calcula a nota final
    matched_df["NOTA_FINAL"] = (matched_df["NOTA_DA_ANÁLISE_CURRICULAR"] * 1) + (matched_df["Nota Objetiva"] * 9)

    # Mantém apenas as colunas relevantes
    final_df = matched_df[["Nome", "NOTA_DA_ANÁLISE_CURRICULAR", "Nota Objetiva", "NOTA_FINAL", "Especialidade"]]

    # Renomeia colunas
    final_df.columns = ["NOME", "NOTA_DA_ANALISE_CURRICULAR", "NOTA_OBJETIVA", "NOTA_FINAL", "ESPECIALIDADE"]

    return final_df


def generate_excel_by_specialty(df, output_file):
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for i, specialty in enumerate(sorted(df['ESPECIALIDADE'].unique())):
            filtered_df = df[df['ESPECIALIDADE'] == specialty]
            filtered_df = filtered_df.sort_values(by="NOTA_FINAL", ascending=False)
            filtered_df = filtered_df.reset_index(drop=True)
            filtered_df.insert(0, "N", 0)
            filtered_df["N"] = filtered_df.index + 1

            filtered_df.rename(columns={'NOTA_DA_ANALISE_CURRICULAR': 'NOTA_CURR', 'NOTA_OBJETIVA': 'NOTA_OBJ'}, inplace=True)

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


def merge(file_notas: str, file_curr: str):
    df_curr = pd.read_csv(file_curr)
    df_notas = pd.read_csv(file_notas)

    print_file_hash(os.getcwd(), file_curr)
    print_file_hash(os.getcwd(), file_notas)
    print(f"Processando notas do currículo em {file_curr} e notas objetivas em {file_notas}... Por favor aguarde.")

    final_df = combine(df_curr, df_notas)
    final_df.sort_values(by="NOTA_FINAL", ascending=False, inplace=True)

    out_file = "notas_pareadas_todas_especialidades.xlsx"
    final_df.to_excel(out_file, index=False)
    print_file_hash(os.getcwd(), out_file)
    print(f"Notas pareadas exportadas para '{out_file}'.")

    out_file = "notas_pareadas_por_especialidades.xlsx"
    generate_excel_by_specialty(final_df, out_file)
    print_file_hash(os.getcwd(), out_file)
    print(f"Notas pareadas por especialidade exportadas para '{out_file}'.")


def main():
    file_notas = "notas_objetivas.csv"
    file_curr = "notas_curriculo.csv"

    for f in [file_notas, file_curr]:
        if not os.path.exists(f):
            print(f"Arquivo não encontrado: {f}")
            break
    else:
        merge(file_notas, file_curr)


if __name__ == '__main__':
    main()
