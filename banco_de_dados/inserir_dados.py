from db_config import conectar_Banco

def inserir_unidades():
    try:
        conn = conectar_Banco()
        cursor = conn.cursor()
        


        ''' Inserir dados
        
        cursor.execute("""
            INSERT INTO Unidades (nome, endereco, latitude, longitude, expediente) VALUES
            (?, ?, ?, ?, ?)
        """, ('UBS 01', 'Rua claro, 100', -23.234235, 60.124145, '14:00 as 16:00'))
        
        cursor.execute("""
            INSERT INTO Unidades (nome, endereco, latitude, longitude, expediente) VALUES
            (?, ?, ?, ?, ?)
        """, ('UBS 02', 'Rua escuro, 101', 40.214335, 80.123259, '14:00 as 16:00'))
        
        '''
        conn.commit()
        conn.close()
        print("Dados inseridos com sucesso na tabela Unidades.")
        
    except Exception as e:
        print("Erro ao inserir dados na tabela Unidades:")
        print(e)

inserir_unidades()
