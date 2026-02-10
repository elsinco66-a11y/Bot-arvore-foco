import os
import json
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Configuração básica
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONFIGURAÇÕES DA ÁRVORE ---
ARQUIVO_DADOS = 'dados_arvore.json'
DECAIMENTO_POR_HORA = 2  # A árvore perde 2% de vida por hora
RECUPERACAO_POR_ACORDO = 10  # A árvore ganha 10% por acordo cumprido

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return {"vida": 100, "ultima_atualizacao": datetime.now().isoformat()}
    try:
        with open(ARQUIVO_DADOS, 'r') as f:
            return json.load(f)
    except:
        return {"vida": 100, "ultima_atualizacao": datetime.now().isoformat()}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w') as f:
        json.dump(dados, f)

def calcular_vida_atual(dados):
    agora = datetime.now()
    ultima_vez = datetime.fromisoformat(dados['ultima_atualizacao'])
    horas_passadas = (agora - ultima_vez).total_seconds() / 3600
    
    perda = horas_passadas * DECAIMENTO_POR_HORA
    nova_vida = max(0, dados['vida'] - perda)
    
    # Atualiza o arquivo para não recalcular a mesma perda duas vezes
    dados['vida'] = nova_vida
    dados['ultima_atualizacao'] = agora.isoformat()
    salvar_dados(dados)
    return nova_vida

def get_emoji_arvore(vida):
    if vida >= 80: return "🌳 (Frondosa!)"
    if vida >= 50: return "🌿 (Saudável)"
    if vida >= 20: return "🍂 (Perdendo folhas... Cuidado!)"
    return "🥀 (SECA! Ajudem a árvore!)"

# --- COMANDOS DO BOT ---

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = carregar_dados()
    vida = calcular_vida_atual(dados)
    emoji = get_emoji_arvore(vida)
    await update.message.reply_text(f"Estado da Árvore do Foco:\n\n{emoji}\nSaúde: {vida:.1f}%")

async def paguei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = carregar_dados()
    vida_atual = calcular_vida_atual(dados) # Atualiza a perda antes de curar
    
    nova_vida = min(100, vida_atual + RECUPERACAO_POR_ACORDO)
    dados['vida'] = nova_vida
    salvar_dados(dados)
    
    emoji = get_emoji_arvore(nova_vida)
    await update.message.reply_text(f"🎉 Boa! Você nutriu nossa árvore!\n\nStatus Atual: {emoji}\nSaúde: {nova_vida:.1f}%")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌳 Bot Jardineiro Ativado! Usem /paguei quando cumprirem um acordo e /status para ver a árvore.")

# --- INICIALIZAÇÃO ---
if __name__ == '__main__':
    # O Render vai fornecer o TOKEN via variável de ambiente
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    if not TOKEN:
        print("Erro: Token não encontrado!")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('paguei', paguei))
        application.add_handler(CommandHandler('status', status))
        

        application.run_polling()
