import pyodbc
import os 
from dotenv import load_dotenv

def conectar_Banco():
    load_dotenv()
    servidor = os.getenv("DB_SERVIDOR")
    nome = os.getenv("DB_NOME")   
    usuario = os.getenv("DB_USUARIO")   
    senha = os.getenv("DB_SENHA")   

    conn_str = (
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={servidor};'
        f'DATABASE={nome};'
        f'UID={usuario};'
        f'PWD={senha};'
        f'TrustServerCertificate=yes;'
    )

    return pyodbc.connect(conn_str)
