import pygame, random
from settings import *
from tile import Tile
from player import Player

class Level:

    def __init__(self, level_data, surface, player_id, multiplayer = False):

        self.display_surface = surface
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.multiplayer = multiplayer
        #make empty dictionary for other player
        self.other_players = {}
        self.player_id = player_id

        if self.player_id == 0:
            start_pos = (500,200)
        else:
            start_pos = (800,200)

        local_is_it = (self.player_id == 0)

        player_sprite = Player(start_pos, player_id, is_it=local_is_it)
        self.player.add(player_sprite)



        self.setup_level(level_data)

        self.world_shift = 0
        #pygame.mixer.music.load("sounds/music/song.mp3")
        #pygame.mixer.music.play(-1)

    def setup_level(self, layout):

        for row_index, row in enumerate(layout):
            for cell_index, cell in enumerate(row):
                x = cell_index * tile_size
                y = row_index * tile_size
                if cell == "x":
                    tile = Tile((x,y),tile_size)
                    self.tiles.add(tile)

    def player_collision(self, local_player, opponent):
        if local_player.rect.colliderect(opponent.rect):
            #Calc overlap on both axes
            overlap_x = min(local_player.rect.right, opponent.rect.right) - max(local_player.rect.left, opponent.rect.left)
            overlap_y = min(local_player.rect.bottom, opponent.rect.bottom) - max(local_player.rect.top, opponent.rect.top)
            #fix axis with smallest overlap ("AABB collision resolution")
            if overlap_x < overlap_y:
                if local_player.rect.centerx < opponent.rect.centerx:
                    local_player.rect.right = opponent.rect.left
                else:
                    local_player.rect.left = opponent.rect.right
            else:
                if local_player.rect.centery < opponent.rect.centery:
                    local_player.rect.bottom = opponent.rect.top
                    local_player.direction.y = 0  # Stop gravity pull
                else:
                    local_player.rect.top = opponent.rect.bottom
                    local_player.direction.y = 0
    def scroll_x(self):
        self.world_shift = 0
        player = self.player.sprite
        self.player.sprite.speed=8
        player_x = player.rect.centerx
        direction_x = player.direction.x

        """old scroll code from platformer game
        if player_x > (screen_width - (screen_width/4)) and direction_x > 0:
            self.world_shift = -5
            player.speed = 0
        elif player_x < screen_width/4 and direction_x < 0:
            self.world_shift = 5
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8"""

    def run(self, network=None, player_id=None):
        global local
        #Update all tiles
        self.tiles.update(self.world_shift)
        self.scroll_x()

        #Update LOCAL player
        self.player.update(self.tiles)
        self.player.draw(self.display_surface)

        local = self.player.sprite
        #update OTHER player
        if self.multiplayer and network:
            try:
                #Send local player pos
                data = f"{player_id}:{local.rect.x},{local.rect.y}"
                reply = network.send(data)

                #seperate it from pos
                if reply and "|" in reply:
                    pos_data, it_status_str = reply.split("|")
                    current_it_id = int(it_status_str)

                    #process pos data
                    if ":" in pos_data:
                        parts = pos_data.split(":")
                        other_id = int(parts[0])

                    #check to make sure not own ID
                    if other_id != self.player_id:
                        coords = parts[1].split(",")
                        rx,ry = map(int, coords)

                        #check if other is it
                        other_is_it = (other_id == current_it_id)

                        if other_id not in self.other_players:
                            self.other_players[other_id] = Player((rx,ry), other_id, is_it=other_is_it)

                        else:
                            #update opp's pos and check it status
                            opp = self.other_players[other_id]
                            opp.rect.topleft = (rx,ry)

                            if opp.is_it != other_is_it:
                                opp.set_it_status(other_is_it)

                    #update local player's it
                    local_is_it = (self.player_id == current_it_id)
                    if local.is_it != local_is_it:
                        local.set_it_status(local_is_it)

            except Exception as e:
                print("Network error:",e)

        #draw players (if they exist)
        self.tiles.draw(self.display_surface)
        self.player.update(self.tiles)
        self.player.draw(self.display_surface)
        for i in self.other_players.values():
            self.display_surface.blit(i.image,i.rect)

        #tagging opration & collision detection
        if self.multiplayer and network and len(self.other_players) == 1:
            #get opp sprite
            opp = next(iter(self.other_players.values()))
            #OUT FOR NOWself.player_collision(local, opp)
            #tagging opperation
            if local.rect.colliderect(opp.rect):
                #local was it
                if local.is_it and local.tag_cooldown <= 0:
                    try:
                        network.send(f"TAG:{self.player_id}")
                    except Exception as e:
                        print("Error sending TAG request", e)
                elif opp.is_it:
                    #no need to send as will be sent by other local player
                    pass

        #detect collisions between player and enemy
        #collided_with = pygame.sprite.spritecollide(self.player.sprite, self.enemies, True)

        #if len(collided_with) > 0:
            #self.player.sprite.lives -= 1
            #
        return

