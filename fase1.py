import math
import os
import random
import pygame

# CONFIGURAÇÕES 16:9 WIDESCREEN
LARGURA_BASE = 960
ALTURA_BASE = 540

# MUNDO EXPANDIDO (COM LIMITES FÍSICOS NAS BORDAS)
LARGURA_MUNDO = 4800
camera_x = 0

# --- GERENCIAMENTO DE MULTITOUCH ---
toques_ativos = {}  # Mapeia finger_id -> (pos_x_base, pos_y_base)

# --- VARIÁVEIS GLOBAIS ---
sprite_pose_ataque = {}
sprite_soco = {}
sprite_pulo = {}  # Sprite da animação de pulo
sprite_projetil_raio = {}
sprite_projetil_fogo = {}
sprites_idle = {}
sprites_raio = {}
sprites_andando_dir = {}
sprites_andando_esq = {}

# --- INIMIGOS E PONTOS FIXOS (10 INIMIGOS) ---
sprites_bandido = {}
sprites_boss = {}
total_bandidos_derrotados = 0
TOTAL_BANDIDOS = 10
bandidos = []

# 10 PONTOS ESPECÍFICOS AO LONGO DO MAPA
PONTOS_SPAWN_BANDIDOS = [400, 800, 1200, 1600, 2000, 2400, 2800, 3200, 3600, 4000]
RAIO_DETECCAO_INIMIGO = 350

boss_ativo = False
boss_derrotado = False
boss = None

# PROJÉTEIS DO BOSS (BOLA DE FOGO)
bolas_fogo_boss = []
TEMPO_RECARGA_FOGO_BOSS = 1200
ultimo_disparo_boss = 0

# Controles Globais de Animação dos Inimigos
frame_animacao_inimigo = 0
tempo_ultimo_frame_inimigo = 0
INTERVALO_ANIMACAO_INIMIGO = 180

raios_ativos = []
VELOCIDADE_RAIO = 8
TEMPO_RECARGA_RAIO = 400
ultimo_disparo = 0

# --- EFEITOS VISUAIS E DANO ---
tempo_flash_player = -1000
DURACAO_FLASH = 180

# --- ESTADOS DE FIM DE JOGO E CRÉDITOS ---
estado_fase = "JOGANDO"
FONTE_FIM_JOGO = None
BOTAO_REINICIAR = pygame.Rect((LARGURA_BASE // 2) - 100, 310, 200, 50)

# --- ESTRUTURA DOS CRÉDITOS ROLANTES ---
creditos_y = ALTURA_BASE
VELOCIDADE_CREDITOS = 0.8  # Velocidade reduzida para rolagem mais suave

TEXTO_CREDITOS = [
    "CHOQUE NO SISTEMA",
    "Versão Beta 1.0",
    "",
    "OBRIGADO POR JOGAR!",
    "",
    "A equipa do Alencar Game Studio agradece do fundo do coração",
    "por teres feito parte do teste Beta 1.0 do Choque no Sistema.",
    "",
    "Cada raio disparado, cada golpe desferido e cada batalha travada",
    "contra as hordas do jogo ajudaram-nos a moldar e a aperfeiçoar esta experiência.",
    "O teu apoio e os teus testes foram fundamentais para ajustar as mecânicas,",
    "equilibrar os desafios e dar vida a este universo.",
    "",
    "O SISTEMA AINDA NÃO DESLIGOU...",
    "",
    "A jornada do nosso herói está longe de terminar.",
    "Estamos a trabalhar a todo o vapor no desenvolvimento final do jogo,",
    "preparando novos cenários, inimigos inéditos e confrontos ainda mais intensos.",
    "",
    "LANÇAMENTO OFICIAL: OUTUBRO DE 2026",
    "",
    "Prepara-te para a versão final completa.",
    "O sistema vai voltar a entrar em curto-circuito muito em breve!",
    "",
    "Desenvolvido por: Lucas Henrique Alencar Freitas",
    "Estúdio: Alencar Game Studio",
    "",
    "Até à próxima batalha!",
    "",
    "Pressione [ESPAÇO] ou Toque para Voltar ao Menu"
]

# --- CONTROLES DE INTERFACE (HUD FIXA NOS CANTOS 16:9) ---
BOTAO_TOQUE_ESQUERDA = pygame.Rect(30, 420, 80, 80)
BOTAO_TOQUE_DIREITA = pygame.Rect(130, 420, 80, 80)
BOTAO_TOQUE_PULO = pygame.Rect(620, 410, 80, 80)
BOTAO_TOQUE_SOCO = pygame.Rect(720, 410, 80, 80)
BOTAO_TOQUE_ATAQUE = pygame.Rect(830, 410, 100, 100)
# Ajuste do botão Menu para o canto superior direito
BOTAO_VOLTAR_MENU = pygame.Rect(LARGURA_BASE - 100, 14, 80, 32)

FONTE_BOTAO = None
atacando = False
tipo_ataque = None  # 'raio' ou 'soco'
tempo_inicio_ataque = 0
DURACAO_ATAQUE = 300

# --- PERSONAGEM (VIDA E ENERGIA) ---
POSICAO_CHAO_Y = 380
player_x = 100
player_y = POSICAO_CHAO_Y
vel_y = 0
GRAVIDADE = 0.8
FORCA_PULO = -14
no_chao = True

vida_maxima = 100
vida_atual = 100

energia_maxima = 100
energia_atual = 100
RECARGA_ENERGIA = 0.15
CUSTO_RAIO = 25

VELOCIDADE = 4
direcao_atual = 1
movendo = False
frame_animacao = 0
tempo_ultimo_frame = 0
INTERVALO_ANIMACAO = 120
volume_sfx = 0.5
cenario = None
som_raio = None


def aplicar_flash_vermelho(superficie_original):
    if superficie_original is None:
        return None
    sprite_flash = superficie_original.copy()
    overlay = pygame.Surface(sprite_flash.get_size(), pygame.SRCALPHA)
    overlay.fill((255, 60, 60, 180))
    sprite_flash.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return sprite_flash


def iniciar_musica_fase1():
    try:
        pygame.mixer.music.load('musica_fase1.mp3')
        pygame.mixer.music.set_volume(volume_sfx)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Aviso ao carregar musica_fase1.mp3: {e}")


def parar_musica_fase1():
    pygame.mixer.music.stop()


def definir_volume(novo_volume):
    global volume_sfx, som_raio
    volume_sfx = novo_volume
    pygame.mixer.music.set_volume(volume_sfx)
    if som_raio:
        som_raio.set_volume(volume_sfx)


def inicializar_bandidos():
    global bandidos
    bandidos.clear()
    for spawn_x in PONTOS_SPAWN_BANDIDOS:
        bandidos.append({
            'rect': pygame.Rect(spawn_x, POSICAO_CHAO_Y + 30, 40, 60),
            'x': float(spawn_x),
            'y': float(POSICAO_CHAO_Y),
            'vida_max': 50,
            'vida_atual': 50,
            'estado': 'idle',
            'olhando': 'esquerda',
            'ativo': False,
            'ultimo_dano': -1000,
            'tempo_dano': -1000
        })


def resetar_fase():
    global player_x, player_y, vel_y, no_chao, vida_atual, energia_atual, direcao_atual, movendo, camera_x
    global total_bandidos_derrotados, boss_ativo, boss, boss_derrotado
    global raios_ativos, bolas_fogo_boss, ultimo_disparo_boss, estado_fase, atacando, tipo_ataque, tempo_flash_player
    global toques_ativos, creditos_y

    player_x = 100
    player_y = POSICAO_CHAO_Y
    vel_y = 0
    no_chao = True
    camera_x = 0
    vida_atual = vida_maxima
    energia_atual = energia_maxima
    direcao_atual = 1
    movendo = False
    atacando = False
    tipo_ataque = None
    tempo_flash_player = -1000
    creditos_y = ALTURA_BASE

    toques_ativos.clear()
    total_bandidos_derrotados = 0
    inicializar_bandidos()

    boss_ativo = False
    boss_derrotado = False
    boss = None
    raios_ativos.clear()
    bolas_fogo_boss.clear()
    ultimo_disparo_boss = 0
    estado_fase = "JOGANDO"


def pular():
    global vel_y, no_chao
    if no_chao:
        vel_y = FORCA_PULO
        no_chao = False


def disparar_soco():
    global atacando, tipo_ataque, tempo_inicio_ataque, boss, total_bandidos_derrotados, boss_derrotado, boss_ativo, estado_fase
    tempo_atual = pygame.time.get_ticks()

    atacando = True
    tipo_ataque = 'soco'
    tempo_inicio_ataque = tempo_atual

    if direcao_atual == 8:
        rect_soco = pygame.Rect(player_x - 30, player_y + 20, 40, 50)
    else:
        rect_soco = pygame.Rect(player_x + 70, player_y + 20, 40, 50)

    for bandido in bandidos[:]:
        if rect_soco.colliderect(bandido['rect']):
            bandido['vida_atual'] -= 15
            bandido['tempo_dano'] = tempo_atual
            empurrao = -30 if direcao_atual == 8 else 30
            bandido['x'] = max(0, min(LARGURA_MUNDO - 60, bandido['x'] + empurrao))
            bandido['rect'].x = int(bandido['x'])

            if bandido['vida_atual'] <= 0:
                bandidos.remove(bandido)
                total_bandidos_derrotados += 1

    if boss_ativo and boss:
        if rect_soco.colliderect(boss['rect']):
            boss['vida_atual'] -= 10
            boss['tempo_dano'] = tempo_atual
            empurrao = -15 if direcao_atual == 8 else 15
            boss['x'] = max(0, min(LARGURA_MUNDO - 80, boss['x'] + empurrao))
            boss['rect'].x = int(boss['x'])

            if boss['vida_atual'] <= 0:
                boss = None
                boss_ativo = False
                boss_derrotado = True
                estado_fase = "CREDITOS"


def disparar_raio():
    global ultimo_disparo, atacando, tipo_ataque, tempo_inicio_ataque, energia_atual
    tempo_atual = pygame.time.get_ticks()

    if (tempo_atual - ultimo_disparo >= TEMPO_RECARGA_RAIO) and (energia_atual >= CUSTO_RAIO):
        ultimo_disparo = tempo_atual
        energia_atual -= CUSTO_RAIO
        atacando = True
        tipo_ataque = 'raio'
        tempo_inicio_ataque = tempo_atual

        if direcao_atual == 8:
            sentido = -1
            lado = 'esquerda'
            spawn_x = player_x - 10
        else:
            sentido = 1
            lado = 'direita'
            spawn_x = player_x + 60

        rect_raio = pygame.Rect(spawn_x, player_y + 20, 60, 40)
        raios_ativos.append({
            'rect': rect_raio,
            'sentido': sentido,
            'lado': lado
        })

        if som_raio:
            som_raio.play()


def disparar_bola_fogo_boss():
    global ultimo_disparo_boss, boss
    tempo_atual = pygame.time.get_ticks()

    if boss and boss['energia_atual'] >= boss['custo_fogo']:
        ultimo_disparo_boss = tempo_atual
        boss['energia_atual'] -= boss['custo_fogo']
        boss['estado'] = 'faca'

        sentido = -1 if boss['olhando'] == 'esquerda' else 1
        spawn_x = boss['x'] - 20 if boss['olhando'] == 'esquerda' else boss['x'] + 60

        rect_fogo = pygame.Rect(spawn_x, POSICAO_CHAO_Y + 25, 50, 30)
        bolas_fogo_boss.append({
            'rect': rect_fogo,
            'sentido': sentido,
            'lado': boss['olhando']
        })


def carregar_assets():
    global cenario, sprites_idle, sprite_pose_ataque, sprite_soco, sprite_pulo, sprite_projetil_raio, sprite_projetil_fogo, FONTE_BOTAO, FONTE_FIM_JOGO, som_raio
    global sprites_andando_dir, sprites_andando_esq, sprites_bandido, sprites_boss

    if not pygame.font.get_init():
        pygame.font.init()
    FONTE_BOTAO = pygame.font.SysFont('Arial', 18, bold=True)
    FONTE_FIM_JOGO = pygame.font.SysFont('Arial', 32, bold=True)

    # Carregamento do Sprite de Pulo
    try:
        img_pulo = pygame.image.load('pulo.png').convert_alpha()
        img_pulo = pygame.transform.smoothscale(img_pulo, (110, 110))
        sprite_pulo['direita'] = img_pulo
        sprite_pulo['esquerda'] = pygame.transform.flip(img_pulo, True, False)
    except Exception as e:
        print(f"Aviso no carregamento de pulo.png: {e}")

    try:
        img_pose = pygame.image.load('raio_direita.png').convert_alpha()
        img_pose = pygame.transform.smoothscale(img_pose, (110, 110))
        sprite_pose_ataque['direita'] = img_pose
        sprite_pose_ataque['esquerda'] = pygame.transform.flip(img_pose, True, False)
    except Exception as e:
        print(f"Aviso no carregamento de raio_direita.png: {e}")

    try:
        img_soco = pygame.image.load('soco_direita.png').convert_alpha()
        img_soco = pygame.transform.smoothscale(img_soco, (110, 110))
        sprite_soco['direita'] = img_soco
        sprite_soco['esquerda'] = pygame.transform.flip(img_soco, True, False)
    except Exception as e:
        print(f"Aviso no carregamento de soco_direita.png: {e}")

    try:
        img_raio = pygame.image.load('raio_dir.png').convert_alpha()
        img_raio = pygame.transform.smoothscale(img_raio, (90, 90))
        sprite_projetil_raio['direita'] = img_raio
        sprite_projetil_raio['esquerda'] = pygame.transform.flip(img_raio, True, False)
    except Exception as e:
        print(f"Aviso no carregamento do projetil: {e}")

    try:
        img_fogo = pygame.image.load('bola_fogo.png').convert_alpha()
        img_fogo = pygame.transform.smoothscale(img_fogo, (80, 50))
        sprite_projetil_fogo['esquerda'] = img_fogo
        sprite_projetil_fogo['direita'] = pygame.transform.flip(img_fogo, True, False)
    except Exception as e:
        print(f"Aviso no carregamento da bola_fogo.png: {e}")

    try:
        imagem_bruta = pygame.image.load('fase1.jpg').convert()
        cenario = pygame.transform.smoothscale(imagem_bruta, (LARGURA_MUNDO, ALTURA_BASE))
    except Exception:
        cenario = None

    for i in range(1, 3):
        try:
            img = pygame.image.load('andando_dir.png').convert_alpha()
            sprites_andando_dir[i] = pygame.transform.smoothscale(img, (110, 110))
            img_esq = pygame.image.load('andando_esq.png').convert_alpha()
            sprites_andando_esq[i] = pygame.transform.smoothscale(img_esq, (110, 110))
        except Exception:
            pass

    for i in range(1, 9):
        try:
            img = pygame.image.load(f'Idle{i}.png').convert_alpha()
            sprites_idle[i] = pygame.transform.smoothscale(img, (110, 110))
        except Exception:
            pass

    try:
        img_andar = pygame.image.load('bandido_andar.png').convert_alpha()
        img_andar = pygame.transform.smoothscale(img_andar, (110, 110))
        sprites_bandido['andar_esq'] = img_andar
        sprites_bandido['andar_dir'] = pygame.transform.flip(img_andar, True, False)

        img_idle = pygame.image.load('bandido_idle.png').convert_alpha()
        img_idle = pygame.transform.smoothscale(img_idle, (110, 110))
        sprites_bandido['idle_esq'] = img_idle
        sprites_bandido['idle_dir'] = pygame.transform.flip(img_idle, True, False)

        img_faca = pygame.image.load('bandido_faca.png').convert_alpha()
        img_faca = pygame.transform.smoothscale(img_faca, (110, 110))
        sprites_bandido['faca_esq'] = img_faca
        sprites_bandido['faca_dir'] = pygame.transform.flip(img_faca, True, False)
    except Exception as e:
        print(f"Aviso no carregamento do bandido: {e}")

    try:
        img_boss_andar = pygame.image.load('boss_andando.png').convert_alpha()
        img_boss_andar = pygame.transform.smoothscale(img_boss_andar, (140, 140))
        sprites_boss['andar_esq'] = img_boss_andar
        sprites_boss['andar_dir'] = pygame.transform.flip(img_boss_andar, True, False)

        try:
            img_boss_idle = pygame.image.load('boss_idle.png').convert_alpha()
            img_boss_idle = pygame.transform.smoothscale(img_boss_idle, (140, 140))
            sprites_boss['idle_esq'] = img_boss_idle
            sprites_boss['idle_dir'] = pygame.transform.flip(img_boss_idle, True, False)
        except Exception:
            sprites_boss['idle_esq'] = sprites_boss['andar_esq']
            sprites_boss['idle_dir'] = sprites_boss['andar_dir']

        img_boss_faca = pygame.image.load('boss_atacando.png').convert_alpha()
        img_boss_faca = pygame.transform.smoothscale(img_boss_faca, (140, 140))
        sprites_boss['faca_esq'] = img_boss_faca
        sprites_boss['faca_dir'] = pygame.transform.flip(img_boss_faca, True, False)
    except Exception as e:
        print(f"Aviso no carregamento do Boss: {e}")

    try:
        som_raio = pygame.mixer.Sound('som_raio.wav')
        som_raio.set_volume(volume_sfx)
    except Exception:
        som_raio = None


def criar_boss():
    global boss
    if boss is None and not boss_derrotado:
        spawn_x = min(LARGURA_MUNDO - 200, player_x + 550)
        boss = {
            'rect': pygame.Rect(spawn_x, POSICAO_CHAO_Y + 20, 50, 70),
            'x': float(spawn_x),
            'y': float(POSICAO_CHAO_Y),
            'vida_max': 200,
            'vida_atual': 200,
            'energia_max': 100,
            'energia_atual': 100,
            'custo_fogo': 30,
            'recarga_energia': 0.10,
            'estado': 'andar',
            'olhando': 'esquerda',
            'ultimo_dano': -1000,
            'tempo_dano': -1000
        }


def atualizar(eventos):
    tempo_atual = pygame.time.get_ticks()

    global player_x, player_y, vel_y, no_chao, direcao_atual, vida_atual, energia_atual, camera_x
    global atacando, tipo_ataque, tempo_inicio_ataque, toques_ativos, ultimo_disparo_boss
    global movendo, frame_animacao, tempo_ultimo_frame
    global frame_animacao_inimigo, tempo_ultimo_frame_inimigo
    global total_bandidos_derrotados, boss_ativo, boss, boss_derrotado, estado_fase, tempo_flash_player
    global creditos_y

    superficie_display = pygame.display.get_surface()
    largura_janela, altura_janela = superficie_display.get_size() if superficie_display else (LARGURA_BASE, ALTURA_BASE)
    escala_x = LARGURA_BASE / largura_janela if largura_janela > 0 else 1.0
    escala_y = ALTURA_BASE / altura_janela if altura_janela > 0 else 1.0

    if energia_atual < energia_maxima:
        energia_atual = min(energia_maxima, energia_atual + RECARGA_ENERGIA)

    for evento in eventos:
        if evento.type == pygame.FINGERDOWN:
            x_base = (evento.x * largura_janela) * escala_x
            y_base = (evento.y * altura_janela) * escala_y
            toques_ativos[evento.finger_id] = (x_base, y_base)

            if BOTAO_VOLTAR_MENU.collidepoint((x_base, y_base)):
                resetar_fase()
                return "menu"

            if estado_fase == "GAME_OVER":
                if BOTAO_REINICIAR.collidepoint((x_base, y_base)):
                    resetar_fase()
                    iniciar_musica_fase1()
                    return None
            elif estado_fase == "CREDITOS":
                resetar_fase()
                return "menu"

        elif evento.type == pygame.FINGERMOTION:
            if evento.finger_id in toques_ativos:
                x_base = (evento.x * largura_janela) * escala_x
                y_base = (evento.y * altura_janela) * escala_y
                toques_ativos[evento.finger_id] = (x_base, y_base)

        elif evento.type == pygame.FINGERUP:
            if evento.finger_id in toques_ativos:
                del toques_ativos[evento.finger_id]

        elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            if evento.type == pygame.MOUSEMOTION and not evento.buttons[0]:
                continue
            pos_x_base = evento.pos[0] * escala_x
            pos_y_base = evento.pos[1] * escala_y
            pos_toque = (pos_x_base, pos_y_base)

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if BOTAO_VOLTAR_MENU.collidepoint(pos_toque):
                    resetar_fase()
                    return "menu"

                if estado_fase == "GAME_OVER":
                    if BOTAO_REINICIAR.collidepoint(pos_toque):
                        resetar_fase()
                        iniciar_musica_fase1()
                        return None
                elif estado_fase == "CREDITOS":
                    resetar_fase()
                    return "menu"

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                resetar_fase()
                return "menu"
            elif estado_fase == "CREDITOS" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                resetar_fase()
                return "menu"
            elif evento.key in (pygame.K_w, pygame.K_UP) and estado_fase == "JOGANDO":
                pular()
            elif evento.key == pygame.K_j and estado_fase == "JOGANDO":
                if not atacando:
                    disparar_soco()
            elif evento.key == pygame.K_SPACE and estado_fase == "JOGANDO":
                if not atacando:
                    disparar_raio()

    if estado_fase == "CREDITOS":
        creditos_y -= VELOCIDADE_CREDITOS
        return None

    if estado_fase != "JOGANDO":
        return None

    if vida_atual <= 0:
        estado_fase = "GAME_OVER"
        return None

    toque_esquerda = False
    toque_direita = False
    toque_pulo = False
    toque_soco = False
    toque_ataque = False

    for pos_toque in toques_ativos.values():
        if BOTAO_TOQUE_ESQUERDA.collidepoint(pos_toque):
            toque_esquerda = True
        elif BOTAO_TOQUE_DIREITA.collidepoint(pos_toque):
            toque_direita = True
        elif BOTAO_TOQUE_PULO.collidepoint(pos_toque):
            toque_pulo = True
        elif BOTAO_TOQUE_SOCO.collidepoint(pos_toque):
            toque_soco = True
        elif BOTAO_TOQUE_ATAQUE.collidepoint(pos_toque):
            toque_ataque = True

    if pygame.mouse.get_pressed()[0]:
        pos_mouse = pygame.mouse.get_pos()
        pos_m = (pos_mouse[0] * escala_x, pos_mouse[1] * escala_y)

        if BOTAO_TOQUE_ESQUERDA.collidepoint(pos_m):
            toque_esquerda = True
        elif BOTAO_TOQUE_DIREITA.collidepoint(pos_m):
            toque_direita = True
        elif BOTAO_TOQUE_PULO.collidepoint(pos_m):
            toque_pulo = True
        elif BOTAO_TOQUE_SOCO.collidepoint(pos_m):
            toque_soco = True
        elif BOTAO_TOQUE_ATAQUE.collidepoint(pos_m):
            toque_ataque = True

    if toque_pulo:
        pular()

    if toque_soco and not atacando:
        disparar_soco()

    if toque_ataque and not atacando:
        disparar_raio()

    if atacando and (tempo_atual - tempo_inicio_ataque > DURACAO_ATAQUE):
        atacando = False
        tipo_ataque = None

    teclas = pygame.key.get_pressed()
    esquerda = teclas[pygame.K_a] or teclas[pygame.K_LEFT] or toque_esquerda
    direita = teclas[pygame.K_d] or teclas[pygame.K_RIGHT] or toque_direita

    if not atacando:
        movendo = esquerda or direita
        dx = 0
        if esquerda:
            dx -= VELOCIDADE
            direcao_atual = 8
        elif direita:
            dx += VELOCIDADE
            direcao_atual = 1

        player_x += dx

    vel_y += GRAVIDADE
    player_y += vel_y

    if player_y >= POSICAO_CHAO_Y:
        player_y = POSICAO_CHAO_Y
        vel_y = 0
        no_chao = True

    # --- LIMITES FÍSICOS DO MAPA ---
    player_x = max(0, min(player_x, LARGURA_MUNDO - 100))

    # --- CÂMERA ACOMPANHA O HERÓI ---
    camera_x = player_x - (LARGURA_BASE // 2) + 55
    camera_x = max(0, min(camera_x, LARGURA_MUNDO - LARGURA_BASE))

    if movendo and no_chao:
        if tempo_atual - tempo_ultimo_frame > INTERVALO_ANIMACAO:
            tempo_ultimo_frame = tempo_atual
            frame_animacao = (frame_animacao + 1) % 3
    else:
        frame_animacao = 0

    if tempo_atual - tempo_ultimo_frame_inimigo > INTERVALO_ANIMACAO_INIMIGO:
        tempo_ultimo_frame_inimigo = tempo_atual
        frame_animacao_inimigo = (frame_animacao_inimigo + 1) % 2

    # --- LÓGICA DOS 10 BANDIDOS ---
    if len(bandidos) > 0:
        player_hitbox_combate = pygame.Rect(player_x + 30, player_y + 30, 40, 60)

        for bandido in bandidos[:]:
            distancia_heroi = abs(bandido['x'] - player_x)

            if not bandido['ativo'] and distancia_heroi <= RAIO_DETECCAO_INIMIGO:
                bandido['ativo'] = True

            if bandido['ativo']:
                if bandido['x'] > player_x:
                    bandido['olhando'] = 'esquerda'
                else:
                    bandido['olhando'] = 'direita'

                if bandido['rect'].colliderect(player_hitbox_combate):
                    bandido['estado'] = 'faca'
                    if tempo_atual - bandido.get('ultimo_dano', -1000) > 1000:
                        vida_atual = max(0, vida_atual - 10)
                        tempo_flash_player = tempo_atual
                        bandido['ultimo_dano'] = tempo_atual

                        empurrao_heroi = -35 if bandido['olhando'] == 'esquerda' else 35
                        player_x = max(0, min(LARGURA_MUNDO - 100, player_x + empurrao_heroi))
                else:
                    estado_movimento = 'andar' if frame_animacao_inimigo == 0 else 'idle'

                    if bandido['x'] > player_x + 30:
                        bandido['x'] -= 1.5
                        bandido['estado'] = estado_movimento
                    elif bandido['x'] < player_x - 30:
                        bandido['x'] += 1.5
                        bandido['estado'] = estado_movimento
                    else:
                        bandido['estado'] = 'idle'

                bandido['x'] = max(0, min(LARGURA_MUNDO - 60, bandido['x']))
                bandido['rect'].x = int(bandido['x'])

                for raio in raios_ativos[:]:
                    if bandido['rect'].colliderect(raio['rect']):
                        bandido['vida_atual'] -= 25
                        bandido['tempo_dano'] = tempo_atual

                        bandido['x'] = max(0, min(LARGURA_MUNDO - 60, bandido['x'] + (raio['sentido'] * 40)))
                        bandido['rect'].x = int(bandido['x'])

                        if raio in raios_ativos:
                            raios_ativos.remove(raio)

                        if bandido['vida_atual'] <= 0:
                            if bandido in bandidos:
                                bandidos.remove(bandido)
                            total_bandidos_derrotados += 1
                            break
            else:
                bandido['estado'] = 'idle'

    # --- LÓGICA DO CHEFÃO ---
    elif not boss_derrotado:
        boss_ativo = True

        if boss is None:
            criar_boss()

        if boss:
            pct_vida_boss = boss['vida_atual'] / boss['vida_max']
            modo_furia = pct_vida_boss < 0.5

            taxa_recarga_boss = boss['recarga_energia'] * (2.0 if modo_furia else 1.0)
            if boss['energia_atual'] < boss['energia_max']:
                boss['energia_atual'] = min(boss['energia_max'], boss['energia_atual'] + taxa_recarga_boss)

            player_hitbox_combate = pygame.Rect(player_x + 30, player_y + 30, 40, 60)
            distancia_x = abs(boss['x'] - player_x)

            recarga_fogo_atual = 600 if modo_furia else 1100
            vel_boss_atual = 3.5 if modo_furia else 2.2

            if boss['x'] > player_x:
                boss['olhando'] = 'esquerda'
            else:
                boss['olhando'] = 'direita'

            # 1. Ataque de Perto
            if boss['rect'].colliderect(player_hitbox_combate):
                boss['estado'] = 'faca'
                if tempo_atual - boss.get('ultimo_dano', -1000) > (600 if modo_furia else 800):
                    vida_atual = max(0, vida_atual - (20 if modo_furia else 15))
                    tempo_flash_player = tempo_atual
                    boss['ultimo_dano'] = tempo_atual

                    empurrao_heroi = -45 if boss['olhando'] == 'esquerda' else 45
                    player_x = max(0, min(LARGURA_MUNDO - 100, player_x + empurrao_heroi))

            # 2. Movimentação e Ataque à Distância
            else:
                pode_atirar = (tempo_atual - ultimo_disparo_boss >= recarga_fogo_atual) and (120 < distancia_x < 500)

                if pode_atirar and random.random() < (0.7 if modo_furia else 0.4):
                    boss['estado'] = 'idle'
                    disparar_bola_fogo_boss()
                else:
                    estado_movimento_boss = 'andar' if frame_animacao_inimigo == 0 else 'idle'

                    if boss['x'] > player_x + 30:
                        boss['x'] -= vel_boss_atual
                        boss['estado'] = estado_movimento_boss
                    elif boss['x'] < player_x - 30:
                        boss['x'] += vel_boss_atual
                        boss['estado'] = estado_movimento_boss

            boss['x'] = max(0, min(LARGURA_MUNDO - 80, boss['x']))
            boss['rect'].x = int(boss['x'])

            for raio in raios_ativos[:]:
                if boss['rect'].colliderect(raio['rect']):
                    boss['vida_atual'] -= 20
                    boss['tempo_dano'] = tempo_atual

                    resistencia_knockback = 10 if modo_furia else 20
                    boss['x'] = max(0, min(LARGURA_MUNDO - 80, boss['x'] + (raio['sentido'] * resistencia_knockback)))
                    boss['rect'].x = int(boss['x'])

                    if raio in raios_ativos:
                        raios_ativos.remove(raio)

                    if boss['vida_atual'] <= 0:
                        boss = None
                        boss_ativo = False
                        boss_derrotado = True
                        estado_fase = "CREDITOS"
                        break

    # --- BOLAS DE FOGO DO BOSS ---
    for fogo in bolas_fogo_boss[:]:
        fogo['rect'].x += fogo['sentido'] * 6

        player_rect = pygame.Rect(player_x + 30, player_y + 30, 40, 60)
        if fogo['rect'].colliderect(player_rect):
            vida_atual = max(0, vida_atual - 20)
            tempo_flash_player = tempo_atual

            player_x = max(0, min(LARGURA_MUNDO - 100, player_x + (fogo['sentido'] * 35)))

            if fogo in bolas_fogo_boss:
                bolas_fogo_boss.remove(fogo)
            continue

        if fogo['rect'].x < camera_x - 100 or fogo['rect'].x > camera_x + LARGURA_BASE + 100:
            if fogo in bolas_fogo_boss:
                bolas_fogo_boss.remove(fogo)

    # --- RAIOS DO JOGADOR ---
    for raio in raios_ativos[:]:
        raio['rect'].x += raio['sentido'] * VELOCIDADE_RAIO

        if raio['rect'].x < camera_x - 100 or raio['rect'].x > camera_x + LARGURA_BASE + 100:
            if raio in raios_ativos:
                raios_ativos.remove(raio)

    return None


def desenhar_botoes_toque(superficie):
    global FONTE_BOTAO
    if FONTE_BOTAO is None:
        FONTE_BOTAO = pygame.font.SysFont('Arial', 18, bold=True)

    # Botão Menu posicionado no canto superior direito
    pygame.draw.rect(superficie, (40, 40, 60), BOTAO_VOLTAR_MENU, border_radius=8)
    pygame.draw.rect(superficie, (0, 230, 255), BOTAO_VOLTAR_MENU, width=1, border_radius=8)
    txt_sair = FONTE_BOTAO.render("MENU", True, (255, 255, 255))
    superficie.blit(txt_sair, (BOTAO_VOLTAR_MENU.centerx - txt_sair.get_width() // 2, BOTAO_VOLTAR_MENU.centery - txt_sair.get_height() // 2))

    pygame.draw.rect(superficie, (0, 230, 255), BOTAO_TOQUE_ESQUERDA, width=2, border_radius=12)
    txt_esq = FONTE_BOTAO.render("<", True, (255, 255, 255))
    superficie.blit(txt_esq, (BOTAO_TOQUE_ESQUERDA.centerx - txt_esq.get_width() // 2, BOTAO_TOQUE_ESQUERDA.centery - txt_esq.get_height() // 2))

    pygame.draw.rect(superficie, (0, 230, 255), BOTAO_TOQUE_DIREITA, width=2, border_radius=12)
    txt_dir = FONTE_BOTAO.render(">", True, (255, 255, 255))
    superficie.blit(txt_dir, (BOTAO_TOQUE_DIREITA.centerx - txt_dir.get_width() // 2, BOTAO_TOQUE_DIREITA.centery - txt_dir.get_height() // 2))

    pygame.draw.rect(superficie, (0, 200, 100), BOTAO_TOQUE_PULO, width=2, border_radius=20)
    txt_pulo = FONTE_BOTAO.render("PULO", True, (0, 255, 120))
    superficie.blit(txt_pulo, (BOTAO_TOQUE_PULO.centerx - txt_pulo.get_width() // 2, BOTAO_TOQUE_PULO.centery - txt_pulo.get_height() // 2))

    pygame.draw.rect(superficie, (255, 100, 0), BOTAO_TOQUE_SOCO, width=2, border_radius=20)
    txt_soco = FONTE_BOTAO.render("SOCO", True, (255, 100, 0))
    superficie.blit(txt_soco, (BOTAO_TOQUE_SOCO.centerx - txt_soco.get_width() // 2, BOTAO_TOQUE_SOCO.centery - txt_soco.get_height() // 2))

    pygame.draw.rect(superficie, (255, 200, 0), BOTAO_TOQUE_ATAQUE, width=2, border_radius=20)
    txt_atq = FONTE_BOTAO.render("RAIO", True, (255, 200, 0))
    superficie.blit(txt_atq, (BOTAO_TOQUE_ATAQUE.centerx - txt_atq.get_width() // 2, BOTAO_TOQUE_ATAQUE.centery - txt_atq.get_height() // 2))


def desenhar_hud(superficie):
    global FONTE_BOTAO
    if FONTE_BOTAO is None:
        FONTE_BOTAO = pygame.font.SysFont('Arial', 18, bold=True)

    largura_barra_max = 200
    altura_barra = 14
    pos_x_barra = 50
    pos_y_vida = 14
    pos_y_energia = 34

    porcentagem_vida = max(0, vida_atual / vida_maxima)
    largura_vida_atual = int(largura_barra_max * porcentagem_vida)

    rect_fundo_vida = pygame.Rect(pos_x_barra, pos_y_vida, largura_barra_max, altura_barra)
    rect_vida = pygame.Rect(pos_x_barra, pos_y_vida, largura_vida_atual, altura_barra)

    pygame.draw.rect(superficie, (150, 0, 0), rect_fundo_vida, border_radius=4)
    pygame.draw.rect(superficie, (0, 220, 0), rect_vida, border_radius=4)
    pygame.draw.rect(superficie, (255, 255, 255), rect_fundo_vida, width=1, border_radius=4)

    porcentagem_energia = max(0, energia_atual / energia_maxima)
    largura_energia_atual = int(largura_barra_max * porcentagem_energia)

    rect_fundo_energia = pygame.Rect(pos_x_barra, pos_y_energia, largura_barra_max, altura_barra)
    rect_energia = pygame.Rect(pos_x_barra, pos_y_energia, largura_energia_atual, altura_barra)

    pygame.draw.rect(superficie, (50, 50, 0), rect_fundo_energia, border_radius=4)
    pygame.draw.rect(superficie, (255, 215, 0), rect_energia, border_radius=4)
    pygame.draw.rect(superficie, (255, 255, 255), rect_fundo_energia, width=1, border_radius=4)

    txt_vida = FONTE_BOTAO.render("HP", True, (255, 255, 255))
    txt_energia = FONTE_BOTAO.render("EP", True, (255, 255, 255))
    superficie.blit(txt_vida, (20, pos_y_vida - 2))
    superficie.blit(txt_energia, (20, pos_y_energia - 2))

    if boss_ativo and boss:
        largura_max_boss = 350
        altura_boss_hp = 14
        altura_boss_ep = 8
        pos_x_boss = (LARGURA_BASE // 2) - (largura_max_boss // 2)
        pos_y_boss_hp = 35
        pos_y_boss_ep = 52

        pct_boss_hp = max(0, boss['vida_atual'] / boss['vida_max'])
        pct_boss_ep = max(0, boss['energia_atual'] / boss['energia_max'])

        modo_furia = pct_boss_hp < 0.5
        largura_atual_boss_hp = int(largura_max_boss * pct_boss_hp)
        largura_atual_boss_ep = int(largura_max_boss * pct_boss_ep)

        cor_barra_boss = (255, 0, 0) if modo_furia else (255, 100, 0)
        texto_titulo_boss = "CHEFÃO - MODO FÚRIA!" if modo_furia else "RAIO DE FOGO (CHEFÃO)"

        pygame.draw.rect(superficie, (80, 0, 0), (pos_x_boss, pos_y_boss_hp, largura_max_boss, altura_boss_hp), border_radius=3)
        pygame.draw.rect(superficie, cor_barra_boss, (pos_x_boss, pos_y_boss_hp, largura_atual_boss_hp, altura_boss_hp), border_radius=3)
        pygame.draw.rect(superficie, (255, 255, 255), (pos_x_boss, pos_y_boss_hp, largura_max_boss, altura_boss_hp), width=1, border_radius=3)

        pygame.draw.rect(superficie, (60, 40, 0), (pos_x_boss, pos_y_boss_ep, largura_max_boss, altura_boss_ep), border_radius=2)
        pygame.draw.rect(superficie, (255, 180, 0), (pos_x_boss, pos_y_boss_ep, largura_atual_boss_ep, altura_boss_ep), border_radius=2)
        pygame.draw.rect(superficie, (255, 255, 255), (pos_x_boss, pos_y_boss_ep, largura_max_boss, altura_boss_ep), width=1, border_radius=2)

        txt_boss = FONTE_BOTAO.render(texto_titulo_boss, True, cor_barra_boss)
        superficie.blit(txt_boss, (LARGURA_BASE // 2 - txt_boss.get_width() // 2, 12))


def desenhar_fim_jogo(superficie):
    global FONTE_FIM_JOGO, FONTE_BOTAO
    if FONTE_FIM_JOGO is None:
        FONTE_FIM_JOGO = pygame.font.SysFont('Arial', 32, bold=True)

    sombra = pygame.Surface((LARGURA_BASE, ALTURA_BASE), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 200))
    superficie.blit(sombra, (0, 0))

    txt_titulo = FONTE_FIM_JOGO.render("GAME OVER", True, (255, 30, 30))
    cor_botao = (200, 40, 40)

    superficie.blit(txt_titulo, (LARGURA_BASE // 2 - txt_titulo.get_width() // 2, 180))

    pygame.draw.rect(superficie, cor_botao, BOTAO_REINICIAR, border_radius=10)
    pygame.draw.rect(superficie, (255, 255, 255), BOTAO_REINICIAR, width=2, border_radius=10)
    txt_btn = FONTE_BOTAO.render("JOGAR DE NOVO", True, (255, 255, 255))
    superficie.blit(txt_btn, (BOTAO_REINICIAR.centerx - txt_btn.get_width() // 2, BOTAO_REINICIAR.centery - txt_btn.get_height() // 2))


def desenhar_creditos(superficie):
    global creditos_y, FONTE_FIM_JOGO, FONTE_BOTAO
    if FONTE_FIM_JOGO is None:
        FONTE_FIM_JOGO = pygame.font.SysFont('Arial', 32, bold=True)
    if FONTE_BOTAO is None:
        FONTE_BOTAO = pygame.font.SysFont('Arial', 18, bold=True)

    sombra = pygame.Surface((LARGURA_BASE, ALTURA_BASE), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 230))
    superficie.blit(sombra, (0, 0))

    espacamento_linha = 32
    y_atual = creditos_y

    for linha in TEXTO_CREDITOS:
        if -40 < y_atual < ALTURA_BASE + 40:
            if "CHOQUE NO SISTEMA" in linha or "O SISTEMA AINDA NÃO DESLIGOU" in linha:
                txt_render = FONTE_FIM_JOGO.render(linha, True, (0, 230, 255))
            elif "OBRIGADO POR JOGAR!" in linha or "LANÇAMENTO OFICIAL" in linha:
                txt_render = FONTE_BOTAO.render(linha, True, (255, 215, 0))
            elif "Lucas Henrique Alencar Freitas" in linha or "Alencar Game Studio" in linha:
                txt_render = FONTE_BOTAO.render(linha, True, (0, 255, 120))
            else:
                txt_render = FONTE_BOTAO.render(linha, True, (255, 255, 255))

            rect_txt = txt_render.get_rect(center=(LARGURA_BASE // 2, int(y_atual)))
            superficie.blit(txt_render, rect_txt)

        y_atual += espacamento_linha


def desenhar(superficie):
    tempo_atual = pygame.time.get_ticks()

    if cenario:
        superficie.blit(cenario, (-camera_x, 0))
    else:
        superficie.fill((30, 30, 30))

    lado_virado = 'esquerda' if direcao_atual == 8 else 'direita'
    flash_hero = (tempo_atual - tempo_flash_player < DURACAO_FLASH)

    sprite_heroi = None
    if atacando:
        if tipo_ataque == 'soco' and lado_virado in sprite_soco:
            sprite_heroi = sprite_soco[lado_virado]
        elif tipo_ataque == 'raio' and lado_virado in sprite_pose_ataque:
            sprite_heroi = sprite_pose_ataque[lado_virado]
    elif not no_chao and lado_virado in sprite_pulo:
        sprite_heroi = sprite_pulo[lado_virado]

    if not sprite_heroi:
        if movendo:
            if frame_animacao == 0 and direcao_atual in sprites_idle:
                sprite_heroi = sprites_idle[direcao_atual]
            elif lado_virado == 'esquerda' and frame_animacao in sprites_andando_esq:
                sprite_heroi = sprites_andando_esq[frame_animacao]
            elif lado_virado == 'direita' and frame_animacao in sprites_andando_dir:
                sprite_heroi = sprites_andando_dir[frame_animacao]
        else:
            if direcao_atual in sprites_idle:
                sprite_heroi = sprites_idle[direcao_atual]

    pos_heroi_x = player_x - camera_x

    if sprite_heroi:
        if flash_hero:
            img_flash = aplicar_flash_vermelho(sprite_heroi)
            if img_flash:
                superficie.blit(img_flash, (pos_heroi_x, player_y))
        else:
            superficie.blit(sprite_heroi, (pos_heroi_x, player_y))
    else:
        pygame.draw.rect(superficie, (255, 0, 0) if flash_hero else (0, 230, 255), (pos_heroi_x + 30, player_y + 30, 40, 60))

    # --- DESENHO DOS 10 BANDIDOS ---
    for bandido in bandidos:
        estado = bandido['estado']
        direcao_b = 'esq' if bandido['olhando'] == 'esquerda' else 'dir'
        chave_sprite = f"{estado}_{direcao_b}"

        flash_bandido = (tempo_atual - bandido.get('tempo_dano', -1000) < DURACAO_FLASH)
        pos_b_x = bandido['rect'].x - camera_x

        if chave_sprite in sprites_bandido:
            sprite_b = sprites_bandido[chave_sprite]
            if flash_bandido:
                img_flash = aplicar_flash_vermelho(sprite_b)
                if img_flash:
                    superficie.blit(img_flash, (pos_b_x - 30, POSICAO_CHAO_Y))
            else:
                superficie.blit(sprite_b, (pos_b_x - 30, POSICAO_CHAO_Y))
        else:
            pygame.draw.rect(superficie, (255, 255, 255) if flash_bandido else (255, 50, 50), (pos_b_x, bandido['rect'].y, bandido['rect'].width, bandido['rect'].height))

        bx = pos_b_x - 10
        by = POSICAO_CHAO_Y - 12
        largura_max_b = 40
        pct_b = max(0, bandido['vida_atual'] / bandido['vida_max'])

        pygame.draw.rect(superficie, (150, 0, 0), (bx, by, largura_max_b, 6), border_radius=2)
        pygame.draw.rect(superficie, (0, 220, 0), (bx, by, int(largura_max_b * pct_b), 6), border_radius=2)
        pygame.draw.rect(superficie, (255, 255, 255), (bx, by, largura_max_b, 6), width=1, border_radius=2)

    # --- DESENHO DO CHEFÃO ---
    if boss_ativo and boss:
        estado = boss['estado']
        direcao_b = 'esq' if boss['olhando'] == 'esquerda' else 'dir'
        chave_sprite = f"{estado}_{direcao_b}"

        flash_boss = (tempo_atual - boss.get('tempo_dano', -1000) < DURACAO_FLASH)
        pos_boss_x = boss['rect'].x - camera_x

        if chave_sprite in sprites_boss:
            sprite_b = sprites_boss[chave_sprite]
            if flash_boss:
                img_flash = aplicar_flash_vermelho(sprite_b)
                if img_flash:
                    superficie.blit(img_flash, (pos_boss_x - 35, POSICAO_CHAO_Y - 10))
            else:
                superficie.blit(sprite_b, (pos_boss_x - 35, POSICAO_CHAO_Y - 10))
        else:
            pygame.draw.rect(superficie, (255, 255, 255) if flash_boss else (255, 100, 0), (pos_boss_x, boss['rect'].y, boss['rect'].width, boss['rect'].height))

    for raio in raios_ativos:
        lado = raio['lado']
        pos_raio_x = raio['rect'].x - camera_x
        if lado in sprite_projetil_raio:
            superficie.blit(sprite_projetil_raio[lado], (pos_raio_x - 10, raio['rect'].y - 20))
        else:
            pygame.draw.rect(superficie, (255, 255, 0), (pos_raio_x, raio['rect'].y, raio['rect'].width, raio['rect'].height))

    for fogo in bolas_fogo_boss:
        lado = fogo['lado']
        pos_fogo_x = fogo['rect'].x - camera_x
        if lado in sprite_projetil_fogo:
            superficie.blit(sprite_projetil_fogo[lado], (pos_fogo_x, fogo['rect'].y - 10))
        else:
            pygame.draw.rect(superficie, (255, 100, 0), (pos_fogo_x, fogo['rect'].y, fogo['rect'].width, fogo['rect'].height))

    desenhar_botoes_toque(superficie)
    desenhar_hud(superficie)

    if estado_fase == "CREDITOS":
        desenhar_creditos(superficie)
    elif estado_fase == "GAME_OVER":
        desenhar_fim_jogo(superficie)


# --- LOOP PRINCIPAL DE EXECUÇÃO ---
if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()

    tela = pygame.display.set_mode((LARGURA_BASE, ALTURA_BASE), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("Choque no Sistema")

    relogio = pygame.time.Clock()
    carregar_assets()
    resetar_fase()
    iniciar_musica_fase1()

    rodando = True
    while rodando:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                rodando = False

        resultado = atualizar(eventos)
        if resultado == "menu":
            break

        desenhar(tela)
        pygame.display.flip()
        relogio.tick(60)

    parar_musica_fase1()
    pygame.quit()