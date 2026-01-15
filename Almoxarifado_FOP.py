import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import sqlite3

# Banco de dados do almoxarifado
def consultar_estoque():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nome, quantidade, localizacao FROM produtos")
    itens = cursor.fetchall()
    conn.close()
    
    # Transforma os dados em uma string para a IA ler
    texto_estoque = "\n".join([f"Item: {i[0]}, Qtd: {i[1]}, Local: {i[2]}" for i in itens])
    return texto_estoque

# 1. Configuração do Gemini
# Substitua pela sua chave de API real
genai.configure(api_key="AIzaSyDUFIlzB4Q3tV0hT4tVYGOxVNIoz7mK5DA")

# Configuração do modelo e do "System Prompt" (Instruções de comportamento)
generation_config = {
    "temperature": 0.3, # Baixa temperatura para respostas mais precisas e menos criativas
    "top_p": 0.95,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    system_instruction="Você é um agente de I.A designado para o Almoxarifado que tem como função ajudar o usuário consultando o estoque de materiais além disso você possui a capacidade de responder dúvidas pertinentes ao Almoxarifado pelo usuário, caso a resposta seja incongruente ou não pertinente ao setor, responda de seguinte forma: \"Desculpe, não entendi o que você falou. Pode repetir?\""
)

# 2. Inicialização do Flask (Servidor Web)
app = Flask(__name__)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    # Recebe a mensagem enviada pelo usuário no WhatsApp
    incoming_msg = request.values.get('Body', '').lower()
    
    # Prepara a resposta do Twilio
    resp = MessagingResponse()
    msg = resp.message()

    try:
        # 3. Processamento com Gemini
        # Aqui enviamos o texto do WhatsApp para a IA
        # No momento de gerar a resposta:
        contexto_estoque = consultar_estoque()
        prompt_completo = f"Estoque Atual:\n{contexto_estoque}\n\nPergunta do Usuário: {incoming_msg}"
        response = model.generate_content(prompt_completo)

        # 4. Tratamento de Exceções e Respostas "Não Sei"
        # O Gemini seguirá o 'system_instruction' definido acima.
        # Mas aqui garantimos que a resposta não seja vazia.
        if response.text:
            resposta_final = response.text
        else:
            resposta_final = "Houve um problema ao processar sua solicitação de estoque. Tente novamente."

    except Exception as e:
        # Caso ocorra erro de conexão ou API
        print(f"Erro: {e}")
        resposta_final = "Sistema momentaneamente indisponível. Por favor, contate o suporte de TI."

    # Envia o texto de volta para o Twilio, que entrega no WhatsApp
    msg.body(resposta_final)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)