# Importamos las librerías necesarias
import pygame       # Para gráficos y manejo del juego
import random       # Para generar números aleatorios
import math         # Para cálculos matemáticos
import sys          # Para salir del juego

# Inicializamos pygame (esto es necesario para empezar a usarlo)
pygame.init()

### CONFIGURACIÓN DEL JUEGO ###

# Tamaño del mapa completo (un área muy grande)
MAP_WIDTH, MAP_HEIGHT = 3000, 3000  # 3000x3000 píxeles

# Tamaño de la ventana que vemos (área visible)
VIEW_WIDTH, VIEW_HEIGHT = 800, 600   # 800x600 píxeles

# Creamos la ventana del juego
screen = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT))
pygame.display.set_caption("Agar.io Clone - Bots Mejorados")

# Definimos colores que usaremos (en formato RGB)
WHITE = (255, 255, 255)  # Blanco para el fondo
BLACK = (0, 0, 0)        # Negro para texto
RED = (255, 0, 0)        # Rojo para game over
BLUE = (0, 0, 255)       # Azul para el jugador

# Colores aleatorios para los bots (enemigos)
COLORS = [
    (255, 100, 100),  # Rojo claro
    (100, 255, 100),  # Verde claro
    (100, 100, 255),  # Azul claro
    (255, 255, 100),  # Amarillo
    (255, 100, 255),  # Rosa
    (100, 255, 255)   # Cian
]

### CLASE DEL JUGADOR ###
class Player:
    """Esta clase representa al jugador principal del juego"""
    
    def __init__(self, x, y):
        """Inicializa al jugador con posición y propiedades iniciales"""
        # Posición inicial (centro del mapa)
        self.x = x
        self.y = y
        
        # Tamaño inicial (radio del círculo)
        self.radius = 30
        
        # Color del jugador (azul)
        self.color = BLUE
        
        # Velocidad base de movimiento
        self.speed = 5
        
        # Puntuación inicial (determina el tamaño)
        self.score = 50
        
        # Desplazamiento de la cámara (para seguir al jugador)
        self.view_offset_x = 0
        self.view_offset_y = 0
    
    def draw(self, screen):
        """Dibuja al jugador en la pantalla"""
        # Calculamos la posición en la pantalla teniendo en cuenta la cámara
        screen_x = self.x - self.view_offset_x
        screen_y = self.y - self.view_offset_y
        
        # Dibujamos el círculo (la célula del jugador)
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)
        
        # Creamos el texto con la puntuación
        font = pygame.font.SysFont(None, 30)  # Fuente tamaño 30
        text = font.render(str(self.score), True, WHITE)  # Texto blanco
        
        # Posicionamos el texto en el centro del jugador
        text_rect = text.get_rect(center=(screen_x, screen_y))
        screen.blit(text, text_rect)
    
    def move(self, keys):
        """Mueve al jugador según las teclas presionadas"""
        # La velocidad disminuye cuando creces (células grandes son más lentas)
        current_speed = max(2, self.speed - self.radius / 25)
        
        # Movimiento con teclas WASD o flechas
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  # Izquierda
            self.x -= current_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:  # Derecha
            self.x += current_speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:    # Arriba
            self.y -= current_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  # Abajo
            self.y += current_speed
        
        # Aseguramos que el jugador no salga del mapa
        self.x = max(self.radius, min(self.x, MAP_WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, MAP_HEIGHT - self.radius))
        
        # Actualizamos el tamaño basado en la puntuación (radio = raíz cuadrada del score)
        self.radius = int(math.sqrt(self.score))
        
        # Actualizamos la cámara para que siga al jugador
        self.update_camera()
    
    def update_camera(self):
        """Ajusta la cámara para seguir al jugador con zoom dinámico"""
        # Calculamos el zoom basado en el tamaño del jugador
        # (células más grandes ven más área del mapa)
        zoom_factor = min(1.0, 100 / self.radius)  # Entre 0.5 y 1.0
        
        # Calculamos cuánto mapa debe ser visible
        visible_width = VIEW_WIDTH / zoom_factor
        visible_height = VIEW_HEIGHT / zoom_factor
        
        # Calculamos dónde debería estar la cámara para centrar al jugador
        target_offset_x = self.x - visible_width / 2
        target_offset_y = self.y - visible_height / 2
        
        # Aseguramos que la cámara no se salga de los límites del mapa
        self.view_offset_x = max(0, min(target_offset_x, MAP_WIDTH - visible_width))
        self.view_offset_y = max(0, min(target_offset_y, MAP_HEIGHT - visible_height))

### CLASE DE LOS BOTS (ENEMIGOS MEJORADOS) ###
class Bot:
    """Esta clase representa a los enemigos controlados por la computadora con comportamiento mejorado"""
    
    def __init__(self, player):
        """Crea un nuevo bot, posiblemente cerca del jugador"""
        # Puntuación inicial aleatoria (entre 30 y 70)
        self.score = random.randint(30, 70)
        
        # Tamaño basado en la puntuación
        self.radius = int(math.sqrt(self.score))
        
        # Posición inicial - 70% de probabilidad de aparecer cerca del jugador
        if random.random() < 0.7:
            offset = random.randint(-500, 500)  # Aleatorio cerca del jugador
            self.x = player.x + offset
            self.y = player.y + offset
        else:
            # 30% de probabilidad de aparecer en cualquier lugar del mapa
            self.x = random.randint(self.radius, MAP_WIDTH - self.radius)
            self.y = random.randint(self.radius, MAP_HEIGHT - self.radius)
        
        # Color aleatorio de la lista de colores
        self.color = random.choice(COLORS)
        
        # Velocidad (los bots más grandes son más lentos)
        self.speed = max(1, 4 - self.radius / 20)
        
        # Dirección inicial aleatoria
        self.direction = random.uniform(0, 2 * math.pi)
        
        # Contador para cambiar de dirección
        self.change_direction_counter = 0
        
        # Objetivo actual (a quién perseguir)
        self.target = None
        
        # Amenaza actual (de quién huir)
        self.flee_target = None
        
        # Comida objetivo cuando no hay otras prioridades (NUEVO)
        self.food_target = None
        
        # Tiempo desde que buscó comida por última vez (NUEVO)
        self.last_food_search = 0

    def draw(self, screen, view_offset_x, view_offset_y):
        """Dibuja el bot en la pantalla, si está visible"""
        # Calculamos la posición en pantalla
        screen_x = self.x - view_offset_x
        screen_y = self.y - view_offset_y
        
        # Solo dibujamos si está dentro o cerca del área visible
        if (-self.radius < screen_x < VIEW_WIDTH + self.radius and 
            -self.radius < screen_y < VIEW_HEIGHT + self.radius):
            
            # Dibujamos el círculo del bot
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)
            
            # Dibujamos su puntuación en el centro
            font = pygame.font.SysFont(None, 30)
            text = font.render(str(self.score), True, WHITE)
            text_rect = text.get_rect(center=(screen_x, screen_y))
            screen.blit(text, text_rect)
    
    def find_nearest_food(self, foods):
        """Encuentra la comida más cercana al bot (NUEVO)"""
        if not foods:
            return None
            
        # Filtramos comida que esté dentro de un rango razonable (optimización)
        visible_foods = [f for f in foods if 
                        abs(f.x - self.x) < 500 and 
                        abs(f.y - self.y) < 500]
        
        if not visible_foods:
            return None
            
        # Encontramos la comida más cercana
        nearest_food = min(visible_foods, 
                          key=lambda f: math.sqrt((f.x - self.x)**2 + (f.y - self.y)**2))
        return nearest_food
    
    def move(self, player, bots, foods):
        """Controla el movimiento y comportamiento mejorado del bot"""
        # Actualizamos tamaño y velocidad
        self.radius = int(math.sqrt(self.score))
        self.speed = max(1, 4 - self.radius / 20)
        
        # Incrementamos contadores
        self.change_direction_counter += 1
        self.last_food_search += 1
        
        # Comportamiento prioritario 1: Huir de amenazas
        potential_threats = [p for p in [player] + bots 
                           if p != self and p.score > self.score * 1.1]
        
        if potential_threats:
            self.flee_target = min(potential_threats, 
                                 key=lambda p: math.sqrt((p.x - self.x)**2 + (p.y - self.y)**2))
            self.target = None
            self.food_target = None
            
            # Calcular dirección para huir
            dx = self.flee_target.x - self.x
            dy = self.flee_target.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                self.direction = math.atan2(dy, dx) + math.pi  # Dirección opuesta
        
        # Comportamiento prioritario 2: Perseguir objetivos más pequeños
        elif self.change_direction_counter >= 90 or random.random() < 0.05:
            potential_targets = [p for p in [player] + bots 
                              if p != self and p.score < self.score * 0.9]
            
            if potential_targets:
                self.target = min(potential_targets, 
                                key=lambda p: math.sqrt((p.x - self.x)**2 + (p.y - self.y)**2))
                self.flee_target = None
                self.food_target = None
                
                # Calcular dirección hacia el objetivo
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    self.direction = math.atan2(dy, dx)
            else:
                # Si no hay objetivos, buscar comida
                self.target = None
                self.flee_target = None
        
        # Comportamiento 3: Buscar comida (cada 60 frames o si no tiene objetivo)
        if (not self.target and not self.flee_target and 
            (self.last_food_search >= 60 or not self.food_target)):
            
            nearest_food = self.find_nearest_food(foods)
            if nearest_food:
                self.food_target = nearest_food
                self.last_food_search = 0
                
                # Calcular dirección hacia la comida
                dx = self.food_target.x - self.x
                dy = self.food_target.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    self.direction = math.atan2(dy, dx)
        
        # Si tenemos un objetivo de comida, perseguirlo
        if self.food_target:
            dx = self.food_target.x - self.x
            dy = self.food_target.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Si la comida fue comida por alguien más o estamos muy cerca
            if distance < self.radius or self.food_target not in foods:
                self.food_target = None
            else:
                self.direction = math.atan2(dy, dx)
        
        # Movimiento aleatorio si no hay objetivos
        if (not self.target and not self.flee_target and not self.food_target and 
            (self.change_direction_counter >= 90 or random.random() < 0.02)):
            
            self.direction = random.uniform(0, 2 * math.pi)
            self.change_direction_counter = 0
        
        # Mover el bot según su dirección actual
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed
        
        # Rebotar en los bordes del mapa
        if self.x < self.radius or self.x > MAP_WIDTH - self.radius:
            self.direction = math.pi - self.direction
        if self.y < self.radius or self.y > MAP_HEIGHT - self.radius:
            self.direction = -self.direction
        
        # Asegurar que no salga del mapa
        self.x = max(self.radius, min(self.x, MAP_WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, MAP_HEIGHT - self.radius))

### CLASE DE LA COMIDA ###
class Food:
    """Esta clase representa los puntos de comida que hacen crecer a las células"""
    
    def __init__(self, player=None):
        """Crea un nuevo punto de comida, posiblemente cerca del jugador"""
        # 80% de probabilidad de aparecer cerca del jugador
        if player and random.random() < 0.8:
            offset = random.randint(-400, 400)
            self.x = player.x + offset
            self.y = player.y + offset
        else:
            # 20% de probabilidad de aparecer en cualquier lugar
            self.x = random.randint(5, MAP_WIDTH - 5)
            self.y = random.randint(5, MAP_HEIGHT - 5)
        
        # Tamaño fijo de la comida
        self.radius = 3
        
        # Color aleatorio (tonos vivos)
        self.color = (
            random.randint(50, 255), 
            random.randint(50, 255), 
            random.randint(50, 255)
        )
        
        # Valor de puntuación (siempre 1)
        self.score = 1
    
    def draw(self, screen, view_offset_x, view_offset_y):
        """Dibuja la comida si está en el área visible"""
        # Posición en pantalla
        screen_x = self.x - view_offset_x
        screen_y = self.y - view_offset_y
        
        # Solo dibujamos si está dentro o cerca del área visible
        if (-self.radius < screen_x < VIEW_WIDTH + self.radius and 
            -self.radius < screen_y < VIEW_HEIGHT + self.radius):
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)

### FUNCIÓN PARA DETECTAR COLISIONES ###
def check_collision(circle1, circle2):
    """Determina si dos círculos están colisionando"""
    # Calculamos la distancia entre centros
    dx = circle1.x - circle2.x
    dy = circle1.y - circle2.y
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Hay colisión si la distancia es menor que la suma de radios
    return distance < circle1.radius + circle2.radius

### FUNCIÓN PRINCIPAL DEL JUEGO ###
def main():
    """Función principal que controla el bucle del juego"""
    # Configuración inicial
    clock = pygame.time.Clock()  # Para controlar la velocidad del juego
    
    # Creamos al jugador en el centro del mapa
    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    
    # Creamos 10 bots (enemigos)
    bots = [Bot(player) for _ in range(15)]
    
    # AUMENTAMOS LA CANTIDAD DE COMIDA INICIAL A 500 (antes eran 200)
    foods = [Food(player) for _ in range(500)]
    
    game_over = False  # Estado del juego
    font = pygame.font.SysFont(None, 36)  # Fuente para texto
    
    ### BUCLE PRINCIPAL DEL JUEGO ###
    while not game_over:
        # Manejo de eventos (como cerrar la ventana)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # Cierra pygame
                sys.exit()     # Cierra el programa
        
        ### LÓGICA DEL JUEGO ###
        if not game_over:
            # 1. Movemos al jugador según las teclas presionadas
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            # 2. Generamos nueva comida más frecuentemente (probabilidad aumentada de 0.02 a 0.05)
            if random.random() < 0.05 and len(foods) < 800:  # Límite aumentado a 800
                foods.append(Food(player))
            
            # 3. Movemos y actualizamos todos los bots (AHORA PASAMOS LA LISTA DE COMIDA)
            for bot in bots[:]:  # Usamos copia para poder modificar la lista
                bot.move(player, bots, foods)
                
                # 4. Verificamos colisiones entre jugador y bots
                if check_collision(player, bot):
                    if player.score > bot.score * 1.1:  # Jugador come al bot
                        player.score += bot.score
                        bots.remove(bot)
                        bots.append(Bot(player))  # Añadimos nuevo bot
                    elif bot.score > player.score * 1.1:  # Bot come al jugador
                        game_over = True
            
            # 5. Verificamos colisiones entre jugador y comida
            for food in foods[:]:
                if check_collision(player, food):
                    player.score += food.score
                    foods.remove(food)
            
            # 6. Verificamos colisiones entre bots y comida
            for bot in bots:
                for food in foods[:]:
                    if check_collision(bot, food):
                        bot.score += food.score
                        foods.remove(food)
            
            # 7. Verificamos colisiones entre bots
            for i in range(len(bots)):
                for j in range(i + 1, len(bots)):
                    if check_collision(bots[i], bots[j]):
                        if bots[i].score > bots[j].score * 1.1:
                            # Bot i come a bot j
                            bots[i].score += bots[j].score
                            bots.remove(bots[j])
                            bots.append(Bot(player))
                            break
                        elif bots[j].score > bots[i].score * 1.1:
                            # Bot j come a bot i
                            bots[j].score += bots[i].score
                            bots.remove(bots[i])
                            bots.append(Bot(player))
                            break
        
        ### DIBUJADO EN PANTALLA ###
        # 1. Limpiamos la pantalla con color blanco
        screen.fill(WHITE)
        
        # 2. Dibujamos toda la comida visible
        for food in foods:
            food.draw(screen, player.view_offset_x, player.view_offset_y)
        
        # 3. Dibujamos todos los bots visibles
        for bot in bots:
            bot.draw(screen, player.view_offset_x, player.view_offset_y)
        
        # 4. Dibujamos al jugador
        player.draw(screen)
        
        # 5. Mostramos la puntuación en la esquina superior izquierda
        score_text = font.render(f"Puntuación: {player.score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        # 6. Mostramos el nivel de zoom actual
        zoom_factor = min(1.0, 100 / player.radius)
        visible_area = f"Zoom: {zoom_factor:.2f}x"
        zoom_text = font.render(visible_area, True, BLACK)
        screen.blit(zoom_text, (10, 50))
        
        # 7. Mostramos mensaje de game over si corresponde
        if game_over:
            game_over_text = font.render("GAME OVER - Presiona R para reiniciar", True, RED)
            screen.blit(game_over_text, (VIEW_WIDTH // 2 - 200, VIEW_HEIGHT // 2))
            
            # Permitimos reiniciar el juego con la tecla R
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
                bots = [Bot(player) for _ in range(10)]
                foods = [Food(player) for _ in range(500)]
                game_over = False
        
        # Actualizamos la pantalla
        pygame.display.flip()
        
        # Controlamos la velocidad del juego (60 fotogramas por segundo)
        clock.tick(60)

# Iniciamos el juego cuando se ejecuta este archivo
if __name__ == "__main__":
    main()