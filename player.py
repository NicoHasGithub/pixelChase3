import pygame, sys
from support import import_folder
from settings import *
from pygame.locals import *

class Player(pygame.sprite.Sprite):

    def __init__(self, pos, player_id, is_it=False):
        super().__init__()
        #Graphics
        self.animations = {}
        #self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.05
        self.font = pygame.font.Font("freesansbold.ttf", 32)
        # game over / you win images
        self.arcade_logo = pygame.image.load("menu/arcadelogo.png")
        self.back = pygame.image.load("menu/keybinds/back_key.png")
        self.winn = pygame.image.load("graphics/game_over/win_game.png")
        self.tag_cooldown = 0

        self.player_id = player_id
        self.is_it = is_it

        #set skin
        self.set_it_status(self.is_it)

        #make sure img exists
        if not hasattr(self, 'image'):
            self.image = pygame.Surface((64,64))
            self.image.fill("red")

        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 1000
        self.jump_speed = -15
        self.status = "idle"

    def set_it_status(self, is_it_new):
        #updates it status and swaps image if necessary
        if not self.is_it and is_it_new:
            self.tag_cooldown = 120 # 2 seconds at 60 FPS
        self.is_it = is_it_new

        #image loading
        image_end = str(self.player_id +1)
        if self.is_it:
            img_file = f"player_"+image_end+"_it.png"
        else:
            img_file = f"player_"+image_end+".png"

        img_path = f"graphics/player_{image_end}/{img_file}"
        #load new img
        try:
            new_img = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(new_img, (64,64))
            #keep pos only if self.rect alr exists
            if hasattr(self, 'rect'):
                old_center = self.rect.center
                self.rect = self.image.get_rect(center=old_center)
        except pygame.error as e:
            print(f"Error loading It image: {img_path}. Error: {e}")
            pass


    def you_win(self):
        clock = pygame.time.Clock()
        pygame.init()
        pygame.display.set_caption('Pixel Chase')
        screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)

        running = True
        while running:
            screen = pygame.display.get_surface()
            screen.fill("white")

            screen.blit(self.arcade_logo, (940, 20))
            screen.blit(self.winn, (300, 200))
            screen.blit(self.back, (100, 550))
            screen.blit(self.exit_gameover, (800, 550))


            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            pygame.display.update()
            clock.tick(fps)

    """def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]"""

    """def import_character_assets(self):
        character_path = "graphics/player/"

        self.animations = {"idle":[], "run":[], "jump":[]}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)"""
    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x=0
        if keys[pygame.K_UP]:
            self.jump()

    def get_status(self):
        if self.direction.y != 0:
            self.status = "jump"
        else:
            if self.direction.x == 0:
                self.status = "idle"
            else:
                self.status = "run"

    def jump(self):
        if self.status != "jump":
            self.direction.y = self.jump_speed

            # sounds
            self.jump_sound = pygame.mixer.Sound("sounds/effects/jump.mp3")

    def horizontal_movement_collision(self, tiles):
        self.rect.x += self.direction.x * self.speed


        for tile in tiles.sprites():
            if tile.rect.colliderect(self.rect):
                if self.direction.x < 0:
                    self.rect.left=tile.rect.right
                elif self.direction.x > 0:
                    self.rect.right=tile.rect.left

    def vertical_movement_collision(self, tiles):
        self.apply_gravity()

        for tile in tiles.sprites():
            if tile.rect.colliderect(self.rect):
                if self.direction.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.direction.y = 0
                    self.status = "idle"
                if self.direction.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.direction.y = 0



    def apply_gravity(self):
        self.direction.y += gravity
        self.rect.y += self.direction.y

    def check_bottom(self):
        pos = self.rect.y
        if pos >= screen_height:
            self.rect.x = 350
            self.rect.y= 0

        else:
            pass


    def display_time(self):
        screen = pygame.display.get_surface()


    def update(self, tiles):
        if self.tag_cooldown > 0:
            self.tag_cooldown -=1
        self.get_input()
        self.horizontal_movement_collision(tiles)
        self.vertical_movement_collision(tiles)
        self.display_time()
        #self.lose_life()
        self.get_status()
        #self.animate()
        self.check_bottom()

