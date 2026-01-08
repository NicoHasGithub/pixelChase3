import pygame

width = 500
height = 400
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

clientNumber = 0

class Player():
    def __init__(self, x, y, width, height, colour):
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.colour = colour
        self.rect = (x,y,width,height)
        self.speed = 5

    def draw(self, win):
        pygame.draw.rect(win, self.colour, self.rect)

    def move(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT]:
            self.x-= self.speed

        if pressed[pygame.K_RIGHT]:
            self.x += self.speed

        if pressed[pygame.K_UP]:
            self.y -= self.speed

        if pressed[pygame.K_DOWN]:
            self.speed += self.speed

def redrawWindow(player):


    win.fill((255,255,255))
    player.draw()
    pygame.display.update()

def main():
    run = True
    p = Player(50,50, 25, 25, (0,255,0))
    while(run):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
        p.move()
        redrawWindow(p)