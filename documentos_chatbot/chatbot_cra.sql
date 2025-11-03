CREATE DATABASE chatbot_cra;

USE chatbot_cra;

CREATE TABLE faq (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pergunta VARCHAR(255) NOT NULL,
    resposta TEXT NOT NULL
);

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    matricula VARCHAR(50),
    email VARCHAR(100),
    tipo_usuario ENUM('aluno', 'professor', 'colaboradro', 'externo') NOT NULL
);

CREATE TABLE interacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    mensagem_usuario TEXT,
    resposta_chatbot TEXT,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

SHOW TABLES;

