import sqlite3

# Conecta ao banco (ou cria se não existir)
conn = sqlite3.connect('estoque.db')
cursor = conn.cursor()

# Cria a tabela de produtos
cursor.execute('''
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    localizacao TEXT NOT NULL
)
''')

# Insere dados de exemplo
estoque_inicial = [
    (1, 'Parafuso Sextavado M8', 500, 'Corredor A, Prateleira 2'),
    (2, 'Luva de Proteção Nitrílica', 50, 'Corredor B, Gaveta 5'),
    (3, 'Fita Isolante 20m', 120, 'Corredor A, Prateleira 1')
]

cursor.executemany('INSERT OR IGNORE INTO produtos VALUES (?,?,?,?)', estoque_inicial)
conn.commit()
conn.close()
print("Banco de dados do almoxarifado pronto!")