"""Prime Senhas: envia UMA mensagem quando uma conta autorizada puder escrever em grupo.
Use apenas em contas/grupos onde a automação seja permitida.
"""
import asyncio
import getpass
import os
import sys
from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, SlowModeWaitError


def configurar():
    print('=== PRIME SENHAS ===')
    print('Use apenas uma conta sua ou com autorização expressa. Nunca compartilhe códigos de login.')
    api_id_txt = os.getenv('TG_API_ID') or input('API ID (my.telegram.org): ').strip()
    api_hash = os.getenv('TG_API_HASH') or getpass.getpass('API HASH: ').strip()
    grupo = os.getenv('TG_GRUPO') or input('Link ou @ do grupo: ').strip()
    mensagem = os.getenv('TG_MENSAGEM') or input('Mensagem exata a enviar: ').strip()
    if not (api_id_txt.isdigit() and api_hash and grupo and mensagem):
        sys.exit('Dados incompletos. Nada foi enviado.')
    return int(api_id_txt), api_hash, grupo, mensagem


async def main():
    api_id, api_hash, grupo, mensagem = configurar()
    # Sessão guardada somente no ambiente local: NÃO publique arquivo .session.
    async with TelegramClient('prime_senhas_sessao', api_id, api_hash) as cliente:
        entidade = await cliente.get_entity(grupo)
        print('Conectado. Verificando se é permitido enviar...')
        estado_anterior = None
        while True:
            try:
                permissoes = await cliente.get_permissions(entidade, 'me')
                permitido = bool(permissoes.send_messages)
                if permitido and estado_anterior is False:
                    print('Envio liberado! Tentando enviar UMA mensagem...')
                    await cliente.send_message(entidade, mensagem)
                    print('Mensagem enviada. Encerrando.')
                    break
                if estado_anterior is None:
                    print('Estado inicial:', 'aberto' if permitido else 'fechado')
                    if permitido:
                        print('Grupo já estava aberto ao iniciar. Não enviando para evitar disparo acidental.')
                if permitido != estado_anterior:
                    print('Grupo:', 'aberto' if permitido else 'fechado')
                estado_anterior = permitido
                await asyncio.sleep(5)
            except FloodWaitError as erro:
                print(f'Telegram solicitou aguardar {erro.seconds} segundos.')
                await asyncio.sleep(erro.seconds + 2)
            except (ChatWriteForbiddenError, SlowModeWaitError) as erro:
                print('Telegram não permitiu o envio:', erro)
                break
            except Exception as erro:
                print('Erro durante verificação:', str(erro))
                await asyncio.sleep(15)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrompido.')
