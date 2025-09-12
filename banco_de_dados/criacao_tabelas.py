from db_config import conectar_Banco

def criar_tabela_unidades():
    try:
        conn = conectar_Banco()
        cursor = conn.cursor()

        cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM sysobjects WHERE name='Unidades' AND xtype='U'
            )
            CREATE TABLE Unidades (
                id_unidade INT PRIMARY KEY IDENTITY(1,1),
                nome VARCHAR(100) NOT NULL,
                endereco VARCHAR(150) NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                expediente VARCHAR(100) NOT NULL
            )
        """)

        conn.commit()
        conn.close()
        print(" Tabela 'Unidades' criada ")

    except Exception as e:
        print("Erro ao criar a tabela ")
        print(e)


def criar_tabela_categorias():
    try:
        conn = conectar_Banco()
        cursor = conn.cursor()

        cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM sysobjects WHERE name='Categorias' AND xtype='U'
            )
            CREATE TABLE Categorias (
                id_categoria INT PRIMARY KEY IDENTITY(1,1),
                codigo_atc VARCHAR(100) NOT NULL,
                descricao VARCHAR(250)
            )
        """)

        conn.commit()
        conn.close()
        print(" Tabela 'Categorias' criada ")

    except Exception as e:
        print("Erro ao criar a tabela ")
        print(e)



def criar_tabela_medicamentos():
    try:
        conn = conectar_Banco()
        cursor = conn.cursor()

        cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM sysobjects WHERE name='Medicamentos' AND xtype='U'
            )
            CREATE TABLE Medicamentos (
                id_medicamento INT PRIMARY KEY IDENTITY(1,1),
                nome VARCHAR(100) NOT NULL,
                id_categoria INT,
               CONSTRAINT FK_Medicamentos_Categorias FOREIGN KEY (id_categoria) REFERENCES Categorias(id_categoria)
            )
        """)

        conn.commit()
        conn.close()
        print(" Tabela 'Medicamentos' criada ")

    except Exception as e:
        print("Erro ao criar a tabela ")
        print(e)


def criar_tabela_disponibilidade_medicamento_unidade():
    try:
        conn = conectar_Banco()
        cursor = conn.cursor()

        cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM sysobjects WHERE name='Disponibilidade_medicamento_unidade' AND xtype='U'
            )
            CREATE TABLE Disponibilidade_medicamento_unidade (
                id_disponibilidade INT PRIMARY KEY IDENTITY(1,1),
                quantidade INT NOT NULL,
                cor VARCHAR(50),
                nivel_disponibilidade VARCHAR(50),
                data DATE,
                id_unidade INT,
                id_medicamento INT,
                CONSTRAINT FK_Disponibilidade_Unidades FOREIGN KEY (id_unidade) REFERENCES Unidades(id_unidade),
                CONSTRAINT FK_Disponibilidade_Medicamentos FOREIGN KEY (id_medicamento) REFERENCES Medicamentos(id_medicamento)
            )
        """)

        conn.commit()
        conn.close()
        print(" Tabela 'Disponibilidade_medicamento_unidade' criada ")

    except Exception as e:
        print("Erro ao criar a tabela ")
        print(e)




criar_tabela_unidades()
criar_tabela_categorias()
criar_tabela_medicamentos()
criar_tabela_disponibilidade_medicamento_unidade()
