import pygame
import random
import math
import sys

# Inicializar pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Agar.io Clone")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
COLORS = [(255, 100, 100), (100, 255, 100), (100, 100, 255), 
          (255, 255, 100), (255, 100, 255), (100, 255, 255)]

# Clase para el jugador
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = BLUE
        self.speed = 5
        self.score = 0
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Mostrar el score (tamaño) del jugador
        font = pygame.font.SysFont(None, 24)
        text = font.render(str(self.score), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
    
    def move(self, keys):
        # Movimiento con WASD o flechas
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed
        
        # Mantener al jugador dentro de los límites
        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

# Clase para los bots
class Bot:
    def __init__(self):
        self.radius = random.randint(10, 30)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.color = random.choice(COLORS)
        self.speed = max(1, 3 - self.radius / 20)
        self.direction = random.uniform(0, 2 * math.pi)
        self.change_direction_counter = 0
        self.score = self.radius
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        font = pygame.font.SysFont(None, 24)
        text = font.render(str(self.score), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
    
    def move(self, player):
        # Cambiar dirección ocasionalmente
        self.change_direction_counter += 1
        if self.change_direction_counter >= 60 or random.random() < 0.01:
            self.direction = random.uniform(0, 2 * math.pi)
            self.change_direction_counter = 0
        
        # Movimiento aleatorio pero a veces hacia el jugador si es más pequeño
        if self.radius > player.radius * 1.1 and random.random() < 0.05:
            # Perseguir al jugador
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                self.direction = math.atan2(dy, dx)
        elif self.radius < player.radius * 0.9 and random.random() < 0.05:
            # Huir del jugador
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                self.direction = math.atan2(dy, dx) + math.pi
        
        # Mover al bot
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed
        
        # Rebotar en los bordes
        if self.x < self.radius or self.x > WIDTH - self.radius:
            self.direction = math.pi - self.direction
        if self.y < self.radius or self.y > HEIGHT - self.radius:
            self.direction = -self.direction
        
        # Asegurarse de que el bot no salga de los límites
        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

# Clase para la comida
class Food:
    def __init__(self):
        self.x = random.randint(5, WIDTH - 5)
        self.y = random.randint(5, HEIGHT - 5)
        self.radius = 5
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Función para verificar colisiones
def check_collision(circle1, circle2):
    dx = circle1.x - circle2.x
    dy = circle1.y - circle2.y
    distance = math.sqrt(dx*dx + dy*dy)
    return distance < circle1.radius + circle2.radius

# Función principal del juego
def main():
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2, HEIGHT // 2)
    bots = [Bot() for _ in range(5)]
    foods = [Food() for _ in range(50)]
    game_over = False
    font = pygame.font.SysFont(None, 36)
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if not game_over:
            # Mover al jugador
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            # Mover bots
            for bot in bots:
                bot.move(player)
                
                # Verificar colisión entre jugador y bot
                if check_collision(player, bot):
                    if player.radius > bot.radius * 1.1:
                        # Jugador come al bot
                        player.score += bot.score
                        player.radius = int(math.sqrt(player.score) + 20)
                        bots.remove(bot)
                        bots.append(Bot())
                    elif bot.radius > player.radius * 1.1:
                        # Bot come al jugador
                        game_over = True
            
            # Verificar colisión entre jugador y comida
            for food in foods[:]:
                if check_collision(player, food):
                    player.score += 1
                    player.radius = int(math.sqrt(player.score) + 20)
                    foods.remove(food)
                    foods.append(Food())
            
            # Verificar colisión entre bots y comida
            for bot in bots:
                for food in foods[:]:
                    if check_collision(bot, food):
                        bot.score += 1
                        bot.radius = int(math.sqrt(bot.score) + 10)
                        bot.speed = max(1, 3 - bot.radius / 20)
                        foods.remove(food)
                        foods.append(Food())
            
            # Verificar colisión entre bots
            for i in range(len(bots)):
                for j in range(i + 1, len(bots)):
                    if check_collision(bots[i], bots[j]):
                        if bots[i].radius > bots[j].radius * 1.1:
                            # Bot i come a bot j
                            bots[i].score += bots[j].score
                            bots[i].radius = int(math.sqrt(bots[i].score) + 10)
                            bots[i].speed = max(1, 3 - bots[i].radius / 20)
                            bots.remove(bots[j])
                            bots.append(Bot())
                            break
                        elif bots[j].radius > bots[i].radius * 1.1:
                            # Bot j come a bot i
                            bots[j].score += bots[i].score
                            bots[j].radius = int(math.sqrt(bots[j].score) + 10)
                            bots[j].speed = max(1, 3 - bots[j].radius / 20)
                            bots.remove(bots[i])
                            bots.append(Bot())
                            break
        
        # Dibujar todo
        screen.fill(WHITE)
        
        for food in foods:
            food.draw(screen)
        
        for bot in bots:
            bot.draw(screen)
        
        player.draw(screen)
        
        if game_over:
            game_over_text = font.render("GAME OVER - Presiona R para reiniciar", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 200, HEIGHT // 2))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                # Reiniciar el juego
                player = Player(WIDTH // 2, HEIGHT // 2)
                bots = [Bot() for _ in range(5)]
                foods = [Food() for _ in range(50)]
                game_over = False
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()