-- Drop das tabelas caso existam, em ordem para respeitar dependências
DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS vendas CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;

-- Criação das tabelas
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    estoque_atual INT NOT NULL DEFAULT 0,
    preco NUMERIC(10,2) NOT NULL
);

CREATE TABLE vendas (
    id SERIAL PRIMARY KEY,
    produto_id INT REFERENCES produtos(id) ON DELETE CASCADE,
    quantidade INT NOT NULL,
    data_venda DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    produto_id INT REFERENCES produtos(id) ON DELETE CASCADE,
    quantidade INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pendente',
    data_pedido DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Inserção de produtos realistas
INSERT INTO produtos (nome, estoque_atual, preco) VALUES
('Saco de Cimento 50kg', 80, 32.90),
('Tijolo Baiano (un)', 500, 1.10),
('Areia Lavada m³', 12, 90.00),
('Brita 1 m³', 10, 110.00),
('Vergalhão 12,5mm 12m', 40, 74.00),
('Telha Cerâmica', 300, 2.85),
('Tinta Acrílica 18L', 25, 189.90),
('Argamassa AC-I 20kg', 60, 18.90),
('Caixa dÁgua 1000L', 8, 499.00),
('Porta de Madeira', 15, 299.90);

-- Vendas simuladas nos últimos 30 dias
DO $$
DECLARE
    i INT;
BEGIN
    FOR i IN 0..29 LOOP
        INSERT INTO vendas (produto_id, quantidade, data_venda) VALUES
        (1, FLOOR(RANDOM() * 5 + 1)::INT, CURRENT_DATE - i),
        (2, FLOOR(RANDOM() * 20 + 10)::INT, CURRENT_DATE - i),
        (3, FLOOR(RANDOM() * 2 + 1)::INT, CURRENT_DATE - i),
        (4, FLOOR(RANDOM() * 2)::INT, CURRENT_DATE - i),
        (5, FLOOR(RANDOM() * 3)::INT, CURRENT_DATE - i),
        (6, FLOOR(RANDOM() * 10 + 5)::INT, CURRENT_DATE - i),
        (7, FLOOR(RANDOM() * 2)::INT, CURRENT_DATE - i),
        (8, FLOOR(RANDOM() * 4)::INT, CURRENT_DATE - i),
        (9, FLOOR(RANDOM() * 1)::INT, CURRENT_DATE - i),
        (10, FLOOR(RANDOM() * 2)::INT, CURRENT_DATE - i);
    END LOOP;
END $$;

-- Pedidos simulados
INSERT INTO pedidos (produto_id, quantidade, status, data_pedido) VALUES
(1, 50, 'pendente', CURRENT_DATE - 2),
(2, 200, 'enviado', CURRENT_DATE - 5),
(3, 3, 'pendente', CURRENT_DATE - 1),
(4, 2, 'cancelado', CURRENT_DATE - 10),
(7, 4, 'pendente', CURRENT_DATE);
