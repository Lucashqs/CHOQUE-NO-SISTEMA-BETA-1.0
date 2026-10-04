import json
import os

ARQUIVO_HIGHSCORE = "highscore.json"

def carregar_highscore():
    """Carrega a maior pontuação salva no arquivo JSON."""
    if not os.path.exists(ARQUIVO_HIGHSCORE):
        return 0
    try:
        with open(ARQUIVO_HIGHSCORE, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get("highscore", 0)
    except Exception as e:
        print(f"Erro ao ler highscore.json: {e}")
        return 0

def salvar_highscore(pontuacao_atual):
    """Verifica e salva a nova pontuação se for maior que a atual."""
    recorde_atual = carregar_highscore()
    if pontuacao_atual > recorde_atual:
        try:
            dados = {"highscore": pontuacao_atual}
            with open(ARQUIVO_HIGHSCORE, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4)
            return pontuacao_atual, True  # Retorna o novo recorde e confirma que foi batido
        except Exception as e:
            print(f"Erro ao salvar highscore.json: {e}")
            return recorde_atual, False
    return recorde_atual, False