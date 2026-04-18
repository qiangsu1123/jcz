import pygame

# Initialize Pygame
pygame.init()

# Set up the game window
screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('JCZ Game')

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()