from db_config import conectar_Banco
import json
from pathlib import Path
from typing import Dict, List
import csv
import unicodedata
from datetime import datetime

ARQ_MEDICAMENTOS = Path("data/medicamentos.csv")

codigo_atc_descricao = {
    "M05": "Anti-osteoporóticos",
    "C07": "Betabloqueadores (para tratamento de hipertensão e doenças cardíacas)",
    "C08": "Bloqueadores dos canais de cálcio (para tratamento de hipertensão e angina)",
    "R03": "Medicamentos para doenças respiratórias (como broncodilatadores)",
    "C09": "Inibidores da enzima conversora de angiotensina (para hipertensão e insuficiência cardíaca)",
    "A10": "Medicamentos para diabetes",
    "C02": "Anti-hipertensivos de outras classes (como anti-hipertensivos diuréticos)",
    "C03": "Diuréticos (para tratamento de hipertensão e insuficiência cardíaca)",
    "J05": "Antivirais de ação direta (para tratamento de infecções virais, como HIV e hepatite)",
    "C10": "Medicamentos para redução de lipídios (como estatinas para colesterol)",
    "C01": "Medicamentos para doenças cardíacas (ex: antiarrítmicos)"
}


medicamentos_atc = {
    "ALENDRONATO DE SODIO 70 MG COMPRIMIDO": "M05",
    "AMIODARONA CLORIDRATO 200 MG COMPRIMIDO": "C01",
    "ANLODIPINO BESILATO 10 MG COMPRIMIDO": "C08",
    "ANLODIPINO BESILATO 5 MG COMPRIMIDO": "C08",
    "ATENOLOL 50 MG COMPRIMIDO": "C07",
    "CAPTOPRIL 25 MG COMPRIMIDO": "C09",
    "CARVEDILOL 12,5 MG COMPRIMIDO": "C07",
    "CARVEDILOL 6,25 MG COMPRIMIDO": "C07",
    "ENALAPRIL MALEATO 5 MG COMPRIMIDO": "C09",
    "ENALAPRIL MALEATO 20 MG COMPRIMIDO":"C09",
    "ESPIRONOLACTONA 100 MG COMPRIMIDO": "C03",
    "ESPIRONOLACTONA 25 MG COMPRIMIDO": "C03",
    "FORMOTEROL 6 MCG + BUDESONIDA 200 MCG PO EM CAPSULA PARA INALACAO":"R03",
    "FORMOTEROL 12 MCG + BUDESONIDA 400 MCG PO EM CAPSULA PARA INALACAO":"R03",
    "FUROSEMIDA 40 MG COMPRIMIDO": "C03",
    "GLICLAZIDA 60 MG COMPRIMIDO DE LIBERACAO PROLONGADA": "A10",
    "HIDROCLOROTIAZIDA 25 MG COMPRIMIDO":"C03",
    "INSULINA HUMANA NPH 100 UI/ML SUSPENSAO INJETAVEL FAM 10     ML": "A10",
    "INSULINA HUMANA NPH 100 UI/ML - SUSPENSAO INJETAVEL EM SISTEMA DE APLICACAO PREENCHIDO 3 ML":"A10",
    "INSULINA HUMANA REGULAR 100 UI/ML CARPULE/TUBETE SUSPENSAO INJETAVEL 3 ML": "A10",
    "INSULINA HUMANA REGULAR 100 UI/ML - SUSPENSAO INJETAVEL EM SISTEMA DE APLICACAO PREENCHIDO 3 ML":"A10",
    "INSULINA HUMANA REGULAR 100 UI/ML SUSPENSAO INJETAVEL FAM   10 ML": "A10",
    "IPRATROPIO BROMETO 0,25 MG/ML (0,025%) SOLUCAO INALANTE GOTAS FRASCO 20 ML": "R03",
    "LOSARTANA POTASSICA 50 MG COMPRIMIDO": "C09",
    "METFORMINA CLORIDRATO 500 MG COMPRIMIDO": "A10",
    "METFORMINA CLORIDRATO 850 MG COMPRIMIDO": "A10",
    "METILDOPA 250 MG COMPRIMIDO": "C02",
    "NIFEDIPINO 20 MG COMPRIMIDO LIBERACAO PROLONGADA": "C08",
    "PROPRANOLOL CLORIDRATO 40 MG COMPRIMIDO": "C07",
    "SINVASTATINA 10 MG COMPRIMIDO": "C10",
    "SINVASTATINA 20 MG COMPRIMIDO": "C10",
    "SINVASTATINA 40 MG COMPRIMIDO":"C10",
    "TAF - TENOFOVIR ALAFENAMIDA 25 MG COMPRIMIDO":"J05"
}




DT = datetime.now()
NOME_ARQUIVO = DT.strftime("%d-%m-%y")


with open(f"data/{NOME_ARQUIVO}.json", 'r', encoding='utf-8') as f:
    data = json.load(f)



def carregar_medicamentos() -> List[Dict[str, str]]:
    meds: List[Dict[str, str]] = []
    with ARQ_MEDICAMENTOS.open("r", encoding="utf-8") as f:
        leitor = csv.reader(f)
        for i, row in enumerate(leitor):
            if not row or len(row) < 2:
                continue
            id_, nome, categoria = row[0].strip(), row[1].strip(),row[2].strip()
            if i == 0 and not id_.isdigit():
                continue
            meds.append({"nome": nome,"categoria": categoria})
    return meds


def inserir_unidades():
    global data
    try:
        conn = conectar_Banco()
        cursor = conn.cursor()
        
        for i in range(len(data)):
            dados_por_unidades = data[i]
            cnes = dados_por_unidades['cnes']

            cursor.execute("SELECT COUNT(*) FROM Unidades WHERE cnes = ?", (cnes,))
            contador = cursor.fetchone()[0]

            if contador == 0:
                cursor.execute("""
                    INSERT INTO Unidades (cnes,nome, logradouro, numero, bairro, cep, latitude, longitude, expediente) VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (dados_por_unidades['cnes'], 
                    dados_por_unidades['nome'], 
                    dados_por_unidades['logradouro'], 
                    dados_por_unidades['numero'], 
                    dados_por_unidades['bairro'],
                    dados_por_unidades['cep'],
                    dados_por_unidades['coordenadas']['lat'], 
                    dados_por_unidades['coordenadas']['lng'], 
                    dados_por_unidades['horario']))
            else: 
                 print(f"Unidade com cnes {cnes} já existe. Pulando inserção.")

        conn.commit()
        conn.close()
        print("Dados inseridos com sucesso na tabela Unidades.")
        
    except Exception as e:
        print("Erro ao inserir dados na tabela Unidades:")
        print(e)

def inserir_categorias():
    global codigo_atc_descricao
    try:
        conn = conectar_Banco()
        cursor = conn.cursor()
        
        for codigo in codigo_atc_descricao:
            descricao = codigo_atc_descricao[codigo]

            cursor.execute("SELECT COUNT(*) FROM Categorias WHERE codigo_atc = ?", (codigo,))
            contador = cursor.fetchone()[0]

            if contador == 0:
                cursor.execute("""
                    INSERT INTO Categorias (codigo_atc,descricao) VALUES
                    (?, ?)
                """, (codigo, descricao))
            else: 
                 print(f"Categoria com codigo atc {codigo} já existe. Pulando inserção.")

        conn.commit()
        conn.close()
        print("Dados inseridos com sucesso na tabela Categorias.")
        
    except Exception as e:
        print("Erro ao inserir dados na tabela Categorias:")
        print(e)


def inserir_medicamentos():
    try:
        conn = conectar_Banco()
        cursor = conn.cursor()
        
        for nome, codigo_atc in medicamentos_atc.items():
            cursor.execute("SELECT COUNT(*) FROM Medicamentos WHERE nome = ?", (nome,))
            contador = cursor.fetchone()[0]
            
            if contador == 0:
                cursor.execute("""
                    INSERT INTO Medicamentos (nome, id_categoria) 
                    VALUES (
                        ?, 
                        (SELECT id_categoria FROM Categorias WHERE codigo_atc = ?)
                    )
                """, (nome, codigo_atc))
            else: 
                print(f"Medicamento '{nome}' já existe. Pulando inserção.")

        conn.commit()
        conn.close()
        print("Dados inseridos com sucesso na tabela Medicamentos.")
        
    except Exception as e:
        print("Erro ao inserir dados na tabela Medicamentos:")
        print(e)




def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


def inserir_disponibilidade_medicamento_unidade():
    global data
    try:
        conn = conectar_Banco()
        cursor = conn.cursor()
        
        for dado in range(len(data)):
            dados_por_unidades = data[dado]
            cnes_unidade = dados_por_unidades['cnes']
            
            for med in range (len(dados_por_unidades['medicamentos'])):
                cada_medicamento = dados_por_unidades['medicamentos'][med]
                nome = cada_medicamento['nome']                
                quantidade = cada_medicamento['quantidade']
                nivel_disponibilidade = cada_medicamento['nivelDisponibilidade']
                cor = cada_medicamento['cor']


                cursor.execute("SELECT id_unidade FROM Unidades WHERE cnes = ?", (cnes_unidade,))
                resultado = cursor.fetchone()
                
                if resultado:
                    id_unidade = resultado[0]  
                else:
                    print(f"Unidade com cnes {cnes_unidade} não encontrada. Pulando inserção.")
                    continue 


                cursor.execute("SELECT id_medicamento FROM Medicamentos WHERE nome = ?", (nome,))
                resultado_medicamento = cursor.fetchone()
                
                if resultado_medicamento:
                    id_medicamento = resultado_medicamento[0]  
                else:
                    
                    continue

                #data_manual = '2025-09-25'
                cursor.execute("""SELECT COUNT(*) FROM Disponibilidade_medicamento_unidade WHERE id_medicamento = ? AND id_unidade = ? AND data = CAST(GETDATE() AS DATE)""", (id_medicamento,id_unidade))
                
                contador = cursor.fetchone()[0]

                if contador == 0:
                     cursor.execute("""
                         INSERT INTO Disponibilidade_medicamento_unidade (quantidade, cor, nivel_disponibilidade, data, id_unidade, id_medicamento) VALUES
                        (?, ?, ?, CAST(GETDATE() AS DATE), ?,?)
             
                        
                    """, (quantidade, nivel_disponibilidade, cor, id_unidade, id_medicamento))
                else: 
                    print(f"Medicamento {nome} já existe na unidade {id_unidade}. Pulando inserção.")

        conn.commit()
        conn.close()
        print("Dados inseridos com sucesso na tabela Disponibilidade_medicamento_unidade.")
        
    except Exception as e:
        print("Erro ao inserir dados na tabela Disponibilidade_medicamento_unidade:")
        print(e)

#inserir_categorias()
#inserir_medicamentos()
inserir_unidades()
inserir_disponibilidade_medicamento_unidade()
