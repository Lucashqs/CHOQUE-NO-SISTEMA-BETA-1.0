import sys
import pygame
import random
import fase1

# --- CONSTANTES DE ESTADO ---
ESTADO_INTRO = "intro"
ESTADO_SPLASH_DEV = "splash_dev"
ESTADO_SPLASH_IMG = "splash_img"
ESTADO_MENU = "menu"
ESTADO_OPCOES = "opcoes"
ESTADO_FASE1 = "fase1"

# --- INICIALIZAÇÃO ---
pygame.init()
pygame.mixer.init()
pygame.font.init()

# RESOLUÇÃO BASE 16:9
LARGURA_BASE = 960
ALTURA_BASE = 540

info_tela = pygame.display.Info()
LARGURA_REAL = info_tela.current_w if info_tela.current_w > 0 else 960 
ALTURA_REAL = info_tela.current_h if info_tela.current_h > 0 else 540

TELA = pygame.display.set_mode((LARGURA_REAL, ALTURA_REAL), pygame.RESIZABLE)
pygame.display.set_caption("CHOQUE NO SISTEMA (16:9 WIDESCREEN)")

SUPERFICIE_BASE = pygame.Surface((LARGURA_BASE, ALTURA_BASE))

# --- CORES ---
COR_FUNDO = (15, 15, 30)
COR_CHOQUE = (0, 230, 255)
COR_TEXTO = (255, 255, 255)
COR_BOTAO = (30, 40, 70)

# --- FONTES ---
FONTE_DEV = pygame.font.SysFont("sans-serif", 28, bold=True)
FONTE_TITULO = pygame.font.SysFont("sans-serif", 48, bold=True)
FONTE_BOTAO = pygame.font.SysFont("sans-serif", 24)
FONTE_TEMPORIZADOR = pygame.font.SysFont("sans-serif", 72, bold=True)
FONTE_INTRO_TEXTO = pygame.font.SysFont("sans-serif", 36, bold=True)

# --- RECURSOS E BOTÕES ---
BOTAO_NOVO_JOGO = pygame.Rect(350, 220, 260, 50)
BOTAO_CARREGAR = pygame.Rect(350, 285, 260, 50)
BOTAO_OPCOES = pygame.Rect(350, 350, 260, 50)
BOTAO_VOLTAR = pygame.Rect(350, 430, 260, 50)
barra_volume = pygame.Rect(350, 280, 260, 20)

volume = 0.5
estado_atual = ESTADO_INTRO
tempo_inicio_estado = pygame.time.get_ticks()
DURACAO_INTRO = 10000  # 10 segundos
DURACAO_SPLASH = 4000 

RELOGIO = pygame.time.Clock()
RODANDO = True

def tocar_musica_menu():
    try:
        pygame.mixer.music.load('musica_menu1.mp3')
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Aviso ao tocar música do menu: {e}")

tocar_musica_menu()

# Imagens
try:
    img_fundo = pygame.image.load('fundo_menu.jpg').convert()
    img_fundo = pygame.transform.scale(img_fundo, (LARGURA_BASE, ALTURA_BASE))
    tem_fundo = True
except Exception:
    tem_fundo = False

try:
    img_splash_dev = pygame.image.load('fundo_menu.png').convert()
    img_splash_dev = pygame.transform.scale(img_splash_dev, (LARGURA_BASE, ALTURA_BASE))
    tem_splash_dev = True
except Exception:
    tem_splash_dev = False

try:
    img_splash = pygame.image.load('fundo_splash2.png').convert()
    img_splash = pygame.transform.scale(img_splash, (LARGURA_BASE, ALTURA_BASE))
    tem_splash = True
except Exception:
    tem_splash = False

if hasattr(fase1, 'carregar_assets'):
    fase1.carregar_assets()


def desenhar_intro(superficie, tempo_decorrido):
    superficie.fill((0, 0, 0))
    
    # Temporizador de 10 a 0 s
    segundos_restantes = max(0, 10 - int(tempo_decorrido // 1000))
    txt_tempo = FONTE_TEMPORIZADOR.render(str(segundos_restantes), True, COR_CHOQUE)
    superficie.blit(txt_tempo, (LARGURA_BASE // 2 - txt_tempo.get_width() // 2, 100))

    # Frases a cada 2 segundos
    frase = ""
    if tempo_decorrido < 2000:
        frase = "prepare-se..."
    elif tempo_decorrido < 4000:
        frase = "uma nova batalha..."
    elif tempo_decorrido < 6000:
        frase = "está prestes a começar."

    if frase:
        txt_frase = FONTE_INTRO_TEXTO.render(frase, True, COR_TEXTO)
        superficie.blit(txt_frase, (LARGURA_BASE // 2 - txt_frase.get_width() // 2, ALTURA_BASE // 2 + 20))


def desenhar_tela_opcoes(superficie):
    texto_opcoes = FONTE_TITULO.render("OPÇÕES", True, COR_CHOQUE)
    superficie.blit(texto_opcoes, (LARGURA_BASE // 2 - texto_opcoes.get_width() // 2, 80))

    texto_vol = FONTE_BOTAO.render(f"Volume: {int(volume * 100)}%", True, (255, 235, 59))
    pos_x = LARGURA_BASE // 2 - texto_vol.get_width() // 2 
    pos_y = 210

    rect_fundo_texto = pygame.Rect(pos_x - 10, pos_y - 5, texto_vol.get_width() + 20, texto_vol.get_height() + 10)
    pygame.draw.rect(superficie, (15, 15, 30), rect_fundo_texto, border_radius=5)
    pygame.draw.rect(superficie, COR_CHOQUE, rect_fundo_texto, width=1, border_radius=5)

    superficie.blit(texto_vol, (pos_x, pos_y))

    largura_preenchimento = int(barra_volume.width * volume)
    rect_preenchimento = pygame.Rect(barra_volume.x, barra_volume.y, largura_preenchimento, barra_volume.height)
    pygame.draw.rect(superficie, COR_CHOQUE, rect_preenchimento, border_radius=5)
    pygame.draw.rect(superficie, COR_TEXTO, barra_volume, width=2, border_radius=5)

    circulo_x = barra_volume.x + largura_preenchimento
    circulo_y = barra_volume.centery
    pygame.draw.circle(superficie, COR_TEXTO, (circulo_x, circulo_y), 12)
    pygame.draw.circle(superficie, COR_CHOQUE, (circulo_x, circulo_y), 8)

    pygame.draw.rect(superficie, COR_BOTAO, BOTAO_VOLTAR, border_radius=10)
    pygame.draw.rect(superficie, COR_CHOQUE, BOTAO_VOLTAR, width=2, border_radius=10)
    txt_voltar = FONTE_BOTAO.render("VOLTAR", True, COR_TEXTO)
    superficie.blit(txt_voltar, (BOTAO_VOLTAR.x + (BOTAO_VOLTAR.width - txt_voltar.get_width()) // 2, BOTAO_VOLTAR.y + (BOTAO_VOLTAR.height - txt_voltar.get_height()) // 2))

def desenhar_splash_dev(superficie):
    if tem_splash_dev:
        superficie.blit(img_splash_dev, (0, 0))
    else:
        superficie.fill((0, 0, 0))

def desenhar_carregando(superficie):
    texto_carregando = FONTE_BOTAO.render("CARREGANDO...", True, (255, 255, 255))
    pos_x = LARGURA_BASE - texto_carregando.get_width() - 20
    pos_y = ALTURA_BASE - texto_carregando.get_height() - 20
    superficie.blit(texto_carregando, (pos_x, pos_y))

def desenhar_raios(superficie):
    if random.randint(0, 100) < 30:
        x_inicio = random.randint(50, LARGURA_BASE - 50)
        y_inicio = random.randint(10, 150)
        pontos = [(x_inicio, y_inicio)]

        for _ in range(4):
            x_inicio += random.randint(-30, 30)
            y_inicio += random.randint(15, 35)
            pontos.append((x_inicio, y_inicio))

        if len(pontos) > 1:
            pygame.draw.lines(superficie, (255, 255, 255), False, pontos, 3)
            pygame.draw.lines(superficie, COR_CHOQUE, False, pontos, 1)


# --- LOOP PRINCIPAL ---
while RODANDO:
    eventos_da_rodada = pygame.event.get()
    tempo_atual = pygame.time.get_ticks()

    for evento in eventos_da_rodada:
        if evento.type == pygame.QUIT:
            RODANDO = False

        elif evento.type == pygame.VIDEORESIZE:
            LARGURA_REAL, ALTURA_REAL = evento.w, evento.h

        elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            if evento.type == pygame.MOUSEMOTION and not evento.buttons[0]:
                continue

            pos_x_base = evento.pos[0] * (LARGURA_BASE / LARGURA_REAL)
            pos_y_base = evento.pos[1] * (ALTURA_BASE / ALTURA_REAL)
            pos_convertida = (pos_x_base, pos_y_base)

            if estado_atual == ESTADO_MENU and evento.type == pygame.MOUSEBUTTONDOWN:
                if BOTAO_NOVO_JOGO.collidepoint(pos_convertida):
                    pygame.mixer.music.stop()
                    
                    if hasattr(fase1, 'resetar_fase'):
                        fase1.resetar_fase()
                    if hasattr(fase1, 'definir_volume'):
                        fase1.definir_volume(volume)
                    if hasattr(fase1, 'iniciar_musica_fase1'):
                        fase1.iniciar_musica_fase1()

                    estado_atual = ESTADO_FASE1

                elif BOTAO_CARREGAR.collidepoint(pos_convertida):
                    print("Carregando jogo...")
                elif BOTAO_OPCOES.collidepoint(pos_convertida):
                    estado_atual = ESTADO_OPCOES

            elif estado_atual == ESTADO_OPCOES:
                if barra_volume.collidepoint(pos_convertida) or (barra_volume.y - 15 <= pos_y_base <= barra_volume.bottom + 15 and barra_volume.x <= pos_x_base <= barra_volume.right):
                    rel_x = pos_x_base - barra_volume.x
                    volume = max(0.0, min(1.0, rel_x / barra_volume.width))
                    
                    pygame.mixer.music.set_volume(volume)
                    if hasattr(fase1, 'definir_volume'):
                        fase1.definir_volume(volume)

                elif evento.type == pygame.MOUSEBUTTONDOWN and BOTAO_VOLTAR.collidepoint(pos_convertida):
                    estado_atual = ESTADO_MENU

    if estado_atual == ESTADO_INTRO:
        tempo_decorrido = tempo_atual - tempo_inicio_estado
        desenhar_intro(SUPERFICIE_BASE, tempo_decorrido)

        if tempo_decorrido >= DURACAO_INTRO:
            estado_atual = ESTADO_SPLASH_DEV
            tempo_inicio_estado = tempo_atual

    elif estado_atual == ESTADO_SPLASH_DEV:
        desenhar_splash_dev(SUPERFICIE_BASE)
        desenhar_carregando(SUPERFICIE_BASE)

        if tempo_atual - tempo_inicio_estado > DURACAO_SPLASH:
            estado_atual = ESTADO_SPLASH_IMG
            tempo_inicio_estado = tempo_atual

    elif estado_atual == ESTADO_SPLASH_IMG:
        if tem_splash:
            SUPERFICIE_BASE.blit(img_splash, (0, 0))
        else:
            SUPERFICIE_BASE.fill((0, 0, 0))

        desenhar_carregando(SUPERFICIE_BASE)

        if tempo_atual - tempo_inicio_estado > DURACAO_SPLASH:
            estado_atual = ESTADO_MENU
            tocar_musica_menu()

    elif estado_atual == ESTADO_MENU:
        if tem_fundo:
            SUPERFICIE_BASE.blit(img_fundo, (0, 0))
        else:
            SUPERFICIE_BASE.fill(COR_FUNDO)

        desenhar_raios(SUPERFICIE_BASE)

        texto_titulo = FONTE_TITULO.render("CHOQUE NO SISTEMA", True, COR_CHOQUE)
        SUPERFICIE_BASE.blit(texto_titulo, (LARGURA_BASE // 2 - texto_titulo.get_width() // 2, 80))

        botoes = [
            (BOTAO_NOVO_JOGO, "Novo Jogo"),
            (BOTAO_CARREGAR, "Carregar"),
            (BOTAO_OPCOES, "Opcoes")
        ]

        for retangulo, texto in botoes:
            pygame.draw.rect(SUPERFICIE_BASE, COR_BOTAO, retangulo, border_radius=10)
            pygame.draw.rect(SUPERFICIE_BASE, COR_CHOQUE, retangulo, width=2, border_radius=10)

            txt_surface = FONTE_BOTAO.render(texto, True, COR_TEXTO)
            txt_x = retangulo.x + (retangulo.width - txt_surface.get_width()) // 2
            txt_y = retangulo.y + (retangulo.height - txt_surface.get_height()) // 2
            SUPERFICIE_BASE.blit(txt_surface, (txt_x, txt_y))

    elif estado_atual == ESTADO_OPCOES:
        if tem_fundo:
            SUPERFICIE_BASE.blit(img_fundo, (0, 0))
        else:
            SUPERFICIE_BASE.fill(COR_FUNDO)

        desenhar_raios(SUPERFICIE_BASE)
        desenhar_tela_opcoes(SUPERFICIE_BASE)

    elif estado_atual == ESTADO_FASE1:
        proximo_estado = fase1.atualizar(eventos_da_rodada)
        
        if proximo_estado == ESTADO_MENU or proximo_estado == "menu":
            if hasattr(fase1, 'parar_musica_fase1'):
                fase1.parar_musica_fase1()
            
            tocar_musica_menu()
            estado_atual = ESTADO_MENU
        else:
            fase1.desenhar(SUPERFICIE_BASE)

    tela_escalada = pygame.transform.smoothscale(SUPERFICIE_BASE, (LARGURA_REAL, ALTURA_REAL))
    TELA.blit(tela_escalada, (0, 0))

    pygame.display.flip()
    RELOGIO.tick(60)

pygame.quit()
sys.exit()