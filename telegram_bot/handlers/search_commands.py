"""
Manejadores para comandos de búsqueda de tokens.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

# Configuración de logging
logger = logging.getLogger(__name__)

async def search_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Busca tokens por nombre, símbolo o creador."""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Por favor, proporciona un término de búsqueda. Ejemplo:\n"
            "/search andy"
        )
        return
    
    search_term = " ".join(context.args).lower()
    
    # Enviar mensaje de espera
    wait_message = await update.message.reply_text(
        "🔍 Buscando tokens...",
    )
    
    try:
        # En una implementación real, buscaríamos en la base de datos
        # Por ahora, usamos datos de ejemplo
        search_results = []
        
        # Simular búsqueda con algunos tokens de ejemplo
        example_tokens = [
            {
                "token_address": "8wnN6EuyqsNvXD5pbF9MErcL2QB1eZ4pTmb4wwMGVXwj",
                "name": "ANDY",
                "symbol": "ANDY",
                "twitter_username": "Andy_On_Sol",
                "notable_followers_count": 27
            },
            {
                "token_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "name": "Samoyed Coin",
                "symbol": "SAMO",
                "twitter_username": "samoyedcoin",
                "notable_followers_count": 42
            },
            {
                "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "name": "USD Coin",
                "symbol": "USDC",
                "twitter_username": "circle",
                "notable_followers_count": 156
            }
        ]
        
        # Filtrar tokens basados en el término de búsqueda
        for token in example_tokens:
            if (search_term in token["name"].lower() or 
                search_term in token["symbol"].lower() or 
                search_term in token["twitter_username"].lower()):
                search_results.append(token)
        
        # Formatear respuesta
        if search_results:
            response = f"🔍 *Resultados para '{search_term}':*\n\n"
            
            for token in search_results:
                response += (
                    f"*{token['name']} ({token['symbol']})*\n"
                    f"👤 @{token['twitter_username']} - 👥 {token['notable_followers_count']} notable followers\n"
                    f"🔗 `{token['token_address']}`\n\n"
                )
        else:
            response = f"❌ No se encontraron tokens para '{search_term}'."
        
        # Eliminar mensaje de espera y enviar respuesta
        await wait_message.delete()
        await update.message.reply_text(response, parse_mode='Markdown')
        
        logger.info(f"Usuario {update.effective_user.id} buscó tokens con término '{search_term}'")
    except Exception as e:
        await wait_message.delete()
        await update.message.reply_text(f"❌ Error al buscar tokens: {str(e)}")
        logger.error(f"Error al buscar tokens con término '{search_term}': {str(e)}") 