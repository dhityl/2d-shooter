import sys, pygame


img  = pygame.image.load('./resources/bomb.png')

WIDTH, HEIGHT = 600, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("cock")



def main():
    global angle
    rx, ry = 200, 100
    xc, yc = 300, 300
    orbit_radius = 10

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)


        screen.blit(img, (500, 500))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()