import pygame
import random

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
SPRITE_SIZE = 50
POWERUP_SIZE = 30
HEALTH_REGEN_SIZE = 30
LASER_SIZE = (5, 20)
JOYSTICK_SENSITIVITY = 2.0

# Initialize joystick
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    print("No joystick found!")
    exit()

# Load images
bg_img = pygame.image.load('milky_way.PNG')
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

snapple_img = pygame.image.load('snapple.PNG')
snapple_img = pygame.transform.scale(snapple_img, (SPRITE_SIZE, SPRITE_SIZE))

hit_effect = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE))
hit_effect.fill((255, 0, 0))

eminem_img = pygame.image.load('eminem.PNG')
eminem_img = pygame.transform.scale(eminem_img, (SPRITE_SIZE, SPRITE_SIZE))

powerup_img = pygame.image.load('powerup.PNG')
powerup_img = pygame.transform.scale(powerup_img, (POWERUP_SIZE, POWERUP_SIZE))

cookie_img = pygame.image.load('cookie.PNG')
cookie_img = pygame.transform.scale(cookie_img, (HEALTH_REGEN_SIZE, HEALTH_REGEN_SIZE))

laser_img = pygame.Surface(LASER_SIZE)
laser_img.fill((255, 255, 255))

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snapple vs Eminem')

# Initialize game variables
def reset_game():
    global snapple_x, snapple_y, eminem_x, eminem_y, powerup_x, powerup_y, cookie_x, cookie_y, snapple_speed, eminem_speed, speed_multiplier, health_points, eminem_health, game_over, lasers, eminem_respawn_timer, hit, shooting_effect, score
    snapple_x, snapple_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    eminem_x, eminem_y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
    powerup_x, powerup_y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
    cookie_x, cookie_y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
    snapple_speed = 5
    eminem_speed = 3
    speed_multiplier = 1  # Reset the speed multiplier to 1
    health_points = 100
    eminem_health = 1000
    game_over = False
    lasers = []
    eminem_respawn_timer = 0
    hit = False
    shooting_effect = False
    score = 0

reset_game()

# Main game loop
clock = pygame.time.Clock()
running = True
eminem_down = False
you_win = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if game_over and keys[pygame.K_SPACE]:
        reset_game()

    if not game_over:
        # Control Snapple with DualSense joystick
        axis_x = joystick.get_axis(0) * JOYSTICK_SENSITIVITY
        axis_y = joystick.get_axis(1) * JOYSTICK_SENSITIVITY
        speed = snapple_speed * speed_multiplier

        snapple_x += axis_x * speed
        snapple_y += axis_y * speed

        # Shooting laser with "X" button
        if joystick.get_button(1):
            lasers.append([snapple_x + SPRITE_SIZE // 2, snapple_y + SPRITE_SIZE])
            shooting_effect = True

        # Update laser positions
        for laser in lasers:
            laser[1] += 10  # Move the laser downward

        # Remove off-screen lasers
        lasers = [laser for laser in lasers if laser[1] < SCREEN_HEIGHT]

        # Check for laser hitting Eminem
        for laser in lasers:
            if abs(laser[0] - eminem_x) < SPRITE_SIZE and abs(laser[1] - eminem_y) < SPRITE_SIZE:
                eminem_health -= 10
                lasers.remove(laser)
                score += 10  # Increase score
                if eminem_health <= 0:
                    eminem_health = 0  # Make sure health doesn't go negative
                    you_win = True
                    game_over = True  # Set game over to true here

        # Make Eminem chase Snapple
        if eminem_x < snapple_x:
            eminem_x += eminem_speed
        if eminem_x > snapple_x:
            eminem_x -= eminem_speed
        if eminem_y < snapple_y:
            eminem_y += eminem_speed
        if eminem_y > snapple_y:
            eminem_y -= eminem_speed

        # Check for power-up collision
        if abs(snapple_x - powerup_x) < POWERUP_SIZE and abs(snapple_y - powerup_y) < POWERUP_SIZE:
            speed_multiplier = min(3, speed_multiplier + 0.5)
            powerup_x, powerup_y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)

        # Check for health regenerator collision
        if abs(snapple_x - cookie_x) < HEALTH_REGEN_SIZE and abs(snapple_y - cookie_y) < HEALTH_REGEN_SIZE:
            health_points = min(100, health_points + 20)
            cookie_x, cookie_y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)

        # Check for Eminem collision
        if abs(snapple_x - eminem_x) < SPRITE_SIZE and abs(snapple_y - eminem_y) < SPRITE_SIZE:
            health_points -= 10
            hit = True
            if health_points <= 0:
                game_over = True

        # Draw background
        screen.blit(bg_img, (0, 0))

        # Draw Snapple
        screen.blit(snapple_img, (snapple_x, snapple_y))
        if hit:
            screen.blit(hit_effect, (snapple_x, snapple_y))
            hit = False
        if shooting_effect:
            pygame.draw.line(screen, (255, 255, 255), (snapple_x + SPRITE_SIZE // 2, snapple_y + SPRITE_SIZE), (snapple_x + SPRITE_SIZE // 2, SCREEN_HEIGHT), 5)
            shooting_effect = False

        # Draw Eminem
        if eminem_down:
            rotated_eminem_img = pygame.transform.rotate(eminem_img, 90)
            screen.blit(rotated_eminem_img, (eminem_x, eminem_y))
            if pygame.time.get_ticks() - eminem_respawn_timer > 5000:  # 5 seconds
                eminem_x, eminem_y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
                eminem_health = 100
                eminem_down = False
                you_win = False
        else:
            screen.blit(eminem_img, (eminem_x, eminem_y))

        screen.blit(powerup_img, (powerup_x, powerup_y))
        screen.blit(cookie_img, (cookie_x, cookie_y))

        # Draw lasers
        for laser in lasers:
            screen.blit(laser_img, (laser[0], laser[1]))

        # Display health points
        font = pygame.font.SysFont(None, 50)
        health_text = font.render(f'Health: {health_points}', True, (255, 255, 255))
        screen.blit(health_text, (10, 10))

        eminem_health_text = font.render(f'Eminem Health: {eminem_health}', True, (255, 255, 255))
        screen.blit(eminem_health_text, (SCREEN_WIDTH - 300, 10))

    else:
        if you_win:
            font = pygame.font.SysFont(None, 74)
            win_text = font.render('YOU WIN!', True, (0, 255, 0))
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))

            score_text = font.render(f'Score: {score}', True, (255, 255, 255))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))

            # Wait for the spacebar to restart
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                reset_game()
                you_win = False  # Reset the "YOU WIN!" state
        else:
            font = pygame.font.SysFont(None, 74)
            text = font.render('GAME OVER', True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            restart_text = font.render('Press Space to Restart', True, (255, 255, 255))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 50))

    pygame.display.update()
    clock.tick(30)

pygame.quit()
