import pygame

# --- VARIÁVEIS GLOBAIS ---
sprite_pose_ataque = {}
sprite_projetil_raio = {}
sprites_idle = {}
sprites_raio = {}

raios_ativos = []
VELOCIDADE_RAIO = 6
TEMPO_RECARGA_RAIO = 400
ultimo_disparo = 0

# --- BOTÕES DE INTERFACE (HUD) ---
BOTAO_TOQUE_ESQUERDA = pygame.Rect(10, 520, 70, 70)
BOTAO_TOQUE_DIREITA = pygame.Rect(90, 520, 70, 70)
BOTAO_TOQUE_ATAQUE = pygame.Rect(260, 520, 80, 80)
BOTAO_VOLTAR_MENU = pygame.Rect(10, 10, 80, 35)

FONTE_BOTAO = None

atacando = False
tempo_inicio_ataque = 0
DURACAO_ATAQUE = 300

# Obstáculos da Fase
OBSTACULOS = [
    pygame.Rect(0, 0, 360, 20),      # Topo
    pygame.Rect(0, 260, 360, 20),    # Plataforma/Parede do Meio
    pygame.Rect(0, 0, 20, 640),      # Esquerda
    pygame.Rect(340, 0, 20, 640),    # Direita
]

# --- CONFIGURAÇÕES DIVERSAS ---
LARGURA_BASE = 360
ALTURA_BASE = 640

# --- VARIÁVEIS DO PERSONAGEM ---
player_x = 130
player_y = 500
VELOCIDADE = 3
direcao_atual = 1 # Direção Inicial

volume_sfx = 0.5
cenario = None
som_raio = None


def definir_volume(novo_volume):
    """Atualiza o volume dos efeitos sonoros da fase."""
    global volume_sfx, som_raio
    volume_sfx = novo_volume
    if som_raio:
        som_raio.set_volume(volume_sfx)


def disparar_raio():
    global ultimo_disparo, atacando, tempo_inicio_ataque
    tempo_atual = pygame.time.get_ticks()

    if tempo_atual - ultimo_disparo >= TEMPO_RECARGA_RAIO:
        ultimo_disparo = tempo_atual
        atacando = True
        tempo_inicio_ataque = tempo_atual

        if direcao_atual in [8, 4, 7]:
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


def carregar_assets():
    global cenario, sprites_idle, sprite_pose_ataque, sprite_projetil_raio, FONTE_BOTAO, som_raio

    if not pygame.font.get_init():
        pygame.font.init()
    FONTE_BOTAO = pygame.font.SysFont('Arial', 18, bold=True)

    # Pose Ataque
    try:
        img_pose = pygame.image.load('raio_direita.png').convert_alpha()
        img_pose = pygame.transform.smoothscale(img_pose, (100, 100))
        sprite_pose_ataque['direita'] = img_pose
        sprite_pose_ataque['esquerda'] = pygame.transform.flip(img_pose, True, False)
    except Exception as e:
        print(f"Erro ao carregar pose de ataque: {e}")

    # Projétil Raio
    try:
        img_raio = pygame.image.load('raio_dir.png').convert_alpha()
        img_raio = pygame.transform.smoothscale(img_raio, (80, 80))
        sprite_projetil_raio['direita'] = img_raio
        sprite_projetil_raio['esquerda'] = pygame.transform.flip(img_raio, True, False)
    except Exception as e:
        print(f"Erro ao carregar projetil de raio: {e}")

    # Cenário
    try:
        imagem_bruta = pygame.image.load('fase1.jpg').convert()
        cenario = pygame.transform.smoothscale(imagem_bruta, (LARGURA_BASE, ALTURA_BASE))
        print("Cenário carregado com sucesso!")
    except Exception as erro:
        cenario = None
        print(f"Erro ao carregar o cenário: {erro}")

    # Sprites Idle
    for i in range(1, 9):
        nome_arquivo = f'Idle{i}.png'
        try:
            img = pygame.image.load(nome_arquivo).convert_alpha()
            sprites_idle[i] = pygame.transform.smoothscale(img, (100, 100))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar {nome_arquivo}: {e}")

    # Áudio do Raio (opcional)
    try:
        som_raio = pygame.mixer.Sound('som_raio.wav')
        som_raio.set_volume(volume_sfx)
    except Exception:
        som_raio = None


def atualizar(eventos):
    """Atualiza a lógica da fase. Retorna 'menu' para voltar ao menu principal."""
    global player_x, player_y, direcao_atual
    global atacando, tempo_inicio_ataque

    tempo_atual = pygame.time.get_ticks()

    toque_esquerda = False
    toque_direita = False
    toque_ataque = False

    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "menu"  # Retorna ao Menu ao pressionar ESC
            elif evento.key == pygame.K_SPACE and not atacando:
                toque_ataque = True

        if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos_mouse = pygame.mouse.get_pos()
            largura_janela, altura_janela = pygame.display.get_surface().get_size()
            pos_x_base = pos_mouse[0] * (LARGURA_BASE / largura_janela)
            pos_y_base = pos_mouse[1] * (ALTURA_BASE / altura_janela)
            pos_toque = (pos_x_base, pos_y_base)

            if BOTAO_VOLTAR_MENU.collidepoint(pos_toque):
                return "menu"

            if BOTAO_TOQUE_ATAQUE.collidepoint(pos_toque) and not atacando:
                toque_ataque = True

    if toque_ataque:
        disparar_raio()

    if atacando and (tempo_atual - tempo_inicio_ataque > DURACAO_ATAQUE):
        atacando = False

    # --- MOVIMENTAÇÃO DO PERSONAGEM ---
    if not atacando:
        if pygame.mouse.get_pressed()[0]:
            pos_mouse = pygame.mouse.get_pos()
            largura_janela, altura_janela = pygame.display.get_surface().get_size()
            pos_x_base = pos_mouse[0] * (LARGURA_BASE / largura_janela)
            pos_y_base = pos_mouse[1] * (ALTURA_BASE / altura_janela)
            pos_toque = (pos_x_base, pos_y_base)

            if BOTAO_TOQUE_ESQUERDA.collidepoint(pos_toque):
                toque_esquerda = True
            elif BOTAO_TOQUE_DIREITA.collidepoint(pos_toque):
                toque_direita = True

        teclas = pygame.key.get_pressed()

        esquerda = teclas[pygame.K_a] or teclas[pygame.K_LEFT] or toque_esquerda
        direita = teclas[pygame.K_d] or teclas[pygame.K_RIGHT] or toque_direita    
        cima = teclas[pygame.K_w] or teclas[pygame.K_UP]
        baixo = teclas[pygame.K_s] or teclas[pygame.K_DOWN]

        # Hitbox reduzida para colisões mais realistas (40x60 centralizada no sprite de 100x100)
        player_hitbox = pygame.Rect(player_x + 30, player_y + 30, 40, 60)

        dx = 0
        if esquerda:
            dx -= VELOCIDADE
        if direita:
            dx += VELOCIDADE

        if dx != 0:
            player_hitbox.x += dx
            if not any(player_hitbox.colliderect(obs) for obs in OBSTACULOS):
                player_x += dx
            else:
                player_hitbox.x -= dx

        dy = 0
        if cima:
            dy -= VELOCIDADE
        if baixo:
            dy += VELOCIDADE

        if dy != 0:
            player_hitbox.y += dy
            if not any(player_hitbox.colliderect(obs) for obs in OBSTACULOS):
                player_y += dy

        # Atualização da direção visual
        if baixo and not (esquerda or direita or cima):
            direcao_atual = 5
        elif cima and not (esquerda or direita or baixo):
            direcao_atual = 2
        elif esquerda and not (cima or baixo or direita):
            direcao_atual = 8
        elif direita and not (cima or baixo or esquerda):
            direcao_atual = 1
        elif cima and esquerda:
            direcao_atual = 4
        elif cima and direita:
            direcao_atual = 3
        elif baixo and esquerda:
            direcao_atual = 7
        elif baixo and direita:
            direcao_atual = 6

    # Limite de tela
    player_x = max(0, min(player_x, LARGURA_BASE - 100))
    player_y = max(0, min(player_y, ALTURA_BASE - 100))

    # --- MOVIMENTAÇÃO E COLISÃO DOS RAIOS ---
    for raio in raios_ativos[:]:
        raio['rect'].x += raio['sentido'] * VELOCIDADE_RAIO

        if raio['rect'].x < -50 or raio['rect'].x > LARGURA_BASE + 50:
            raios_ativos.remove(raio)
            continue

        if any(raio['rect'].colliderect(obs) for obs in OBSTACULOS):
            raios_ativos.remove(raio)

    return None


def desenhar_botoes_toque(superficie):
    global FONTE_BOTAO

    if FONTE_BOTAO is None:
        FONTE_BOTAO = pygame.font.SysFont('Arial', 18, bold=True)

    # Botão Sair / Voltar ao Menu
    pygame.draw.rect(superficie, (40, 40, 60), BOTAO_VOLTAR_MENU, border_radius=8)
    pygame.draw.rect(superficie, (0, 230, 255), BOTAO_VOLTAR_MENU, width=1, border_radius=8)
    txt_sair = FONTE_BOTAO.render("MENU", True, (255, 255, 255))
    superficie.blit(txt_sair, (BOTAO_VOLTAR_MENU.centerx - txt_sair.get_width() // 2, BOTAO_VOLTAR_MENU.centery - txt_sair.get_height() // 2))

    # Botão Esquerda
    pygame.draw.rect(superficie, (0, 230, 255), BOTAO_TOQUE_ESQUERDA, width=2, border_radius=10)
    txt_esq = FONTE_BOTAO.render("<", True, (255, 255, 255))
    superficie.blit(txt_esq, (BOTAO_TOQUE_ESQUERDA.centerx - txt_esq.get_width() // 2, BOTAO_TOQUE_ESQUERDA.centery - txt_esq.get_height() // 2))

    # Botão Direita
    pygame.draw.rect(superficie, (0, 230, 255), BOTAO_TOQUE_DIREITA, width=2, border_radius=10)
    txt_dir = FONTE_BOTAO.render(">", True, (255, 255, 255))
    superficie.blit(txt_dir, (BOTAO_TOQUE_DIREITA.centerx - txt_dir.get_width() // 2, BOTAO_TOQUE_DIREITA.centery - txt_dir.get_height() // 2))

    # Botão Ataque
    pygame.draw.rect(superficie, (255, 200, 0), BOTAO_TOQUE_ATAQUE, width=2, border_radius=15)
    txt_atq = FONTE_BOTAO.render("RAIO", True, (255, 200, 0))
    superficie.blit(txt_atq, (BOTAO_TOQUE_ATAQUE.centerx - txt_atq.get_width() // 2, BOTAO_TOQUE_ATAQUE.centery - txt_atq.get_height() // 2))


def desenhar(superficie):
    if cenario:
        superficie.blit(cenario, (0, 0))
    else:
        superficie.fill((30, 30, 30))

    lado_virado = 'esquerda' if direcao_atual in [8, 4, 7] else 'direita'

    # Renderiza o personagem
    if atacando and lado_virado in sprite_pose_ataque:
        superficie.blit(sprite_pose_ataque[lado_virado], (player_x, player_y))
    else:
        if direcao_atual in sprites_idle:
            superficie.blit(sprites_idle[direcao_atual], (player_x, player_y))
        else:
            pygame.draw.rect(superficie, (0, 230, 255), (player_x + 30, player_y + 30, 40, 60))

    # Renderiza projéteis
    for raio in raios_ativos:
        lado = raio['lado']
        if lado in sprite_projetil_raio:
            superficie.blit(sprite_projetil_raio[lado], (raio['rect'].x - 10, raio['rect'].y - 20))
        else:
            pygame.draw.rect(superficie, (255, 255, 0), raio['rect'])

    desenhar_botoes_toque(superficie)