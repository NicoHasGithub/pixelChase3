from level import Level
from player import *
from pygame.locals import *
from tkinter import *
import pygame
import sys
from tkinter import messagebox
import json
from network import Network


clock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption('Pixel Chase')
screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)


#Set up network connection
network = None
multiplayer = False
player_id = 0
try:
    host_ip = input("Enter server IP (leave blank for localhost: ").strip() or "localhost"


    network = Network(host= host_ip, port = 5555)

    if network.id is None:
        raise ConnectionError("Failed to connect to server")

    player_id = int(network.id) #either 0 or 1, controls who hosts the game
    multiplayer = True

except Exception as error:
    print("Could not start multiplayer" + str(error))
    multiplayer = False

#json file management
def load_log():
    with open("game_log.json", "r") as f:
        return json.load(f)

def save_games(data):
    with open("game_log.json", "w") as f:
        return json.dump(data, f, indent=2)

def add_log(hname, pword):
    data = load_log()
    for game in data:
        if game["host_name"].lower() == hname.lower() and game["password"] == pword:
            return False  # Duplicate game
    new_game = {
        "host_name": hname,
        "password": pword,
        "active": True,
        "players_connected": 1
    }
    data.append(new_game)
    save_games(data)
    return True

def join_game_log(hname, pword):
    data = load_log()
    for game in data:
        if game["host_name"].lower() == hname.lower() and game["password"] == pword and game["active"]:
            game["players_connected"] += 1
            if game["players_connected"] >= 2:
                game["active"] = False  # Game ready
            save_games(data)
            return True
    return False

#end of json mgment

#deafult game call
game_state = {
        "level": None,
        "network": None,
        "player_id": None,
        "multiplayer": False
    }

#deafult lobby call
lobby_state = {
        "username": None,
        "password": None
}

#fonts
font = pygame.font.SysFont(None, 76)
font1 = pygame.font.Font("freesansbold.ttf", 32)
retroFont = pygame.font.Font("menu/fonts/retrofont.ttf", 75)
retroSmall = pygame.font.Font("menu/fonts/retrofont.ttf", 36)

#misc variables

time = 0
status = 1 
winner_id = None


#menu images


start_game = pygame.image.load("menu/startgamefinal.png")
controls = pygame.image.load("menu/controls_game.png")
quit_b = pygame.image.load("menu/quit_button.png")
create_g = pygame.image.load("menu/create_game.png")
join_g = pygame.image.load("menu/join_game.png")
start_g = pygame.image.load("menu/start_game_bt.png")

#new menu imgs
bg_img = pygame.image.load("menu/game_bg.jpg")

#high score images
highscore = pygame.image.load("menu/high_scores/high_score.png")
hs_title = pygame.image.load("menu/high_scores/highscore_title.png")
nohs = pygame.image.load("menu/high_scores/no_hs.png")

#settings / controls images
control = pygame.image.load("menu/keybinds/controls.png")
back = pygame.image.load("menu/keybinds/back_key.png")

#game over images
playagain = pygame.image.load("graphics/game_over/play_again.png")
exit_gameover = pygame.image.load("graphics/game_over/exitgameover.png")

#game_images
background_image = pygame.image.load("graphics/background/backgroundclouds.png")

#game over images
game__over = pygame.image.load("graphics/game_over/gameover.png")
playagain = pygame.image.load("graphics/game_over/play_again.png")
exit_gameover = pygame.image.load("graphics/game_over/exitgameover.png")

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x,y)
    surface.blit(textobj, textrect)

click = False

def main_menu():
    global time, status, click
    while True:

        screen.fill("white")


        mx, my = pygame.mouse.get_pos()
        screen.blit(bg_img, (0, 0))
        button_1 = pygame.Rect(475, 300, 300, 50)
        button_2 = pygame.Rect(475, 400, 300, 40)
        button_3 = pygame.Rect(475, 500, 300, 40)
        button_4 = pygame.Rect(475, 600, 300, 50)
        if button_1.collidepoint((mx,my)):
            if click:
                status = 4
                return
        if button_2.collidepoint((mx,my)):
            if click:
                status = 5
                return
        if button_3.collidepoint((mx,my)):
            if click:
                status = 6
                return
        if button_4.collidepoint((mx,my)):
            if click:
                sys.exit()
        draw_text('Pixel Chase', retroFont, (255,255,255), screen, 200, 70)
        pygame.draw.rect(screen, (255,0,0), button_1)
        pygame.draw.rect(screen, (255, 0, 0), button_2)
        pygame.draw.rect(screen, (255, 0, 0), button_3)
        pygame.draw.rect(screen, (255, 0, 0), button_4)
        screen.blit(create_g, (475, 300))
        screen.blit(join_g, (475, 400))
        screen.blit(controls, (475, 500))
        screen.blit(quit_b, (475, 600))

        click = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click= True

        pygame.display.update()
        clock.tick(fps)

def game(level, network, player_id, multiplayer):
    global time, status, winner_id
    time = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        screen.fill("black")
        screen.blit(background_image, (0, 0))

        if multiplayer and network:
            level.run(network=network, player_id=player_id)
        else:
            level.run(None, 0)

        text_1 = font1.render("time left: " + str(int(120 - (time / 60))), True, (0, 0, 0))
        screen.blit(text_1, (64, 0))

        if time >= (20*60):
            if level.player.sprite.is_it:
                winner_id = 1- player_id
            else:
                winner_id = player_id

            status = 3
            return

        pygame.display.update()
        clock.tick(fps)
        time += 1

def lobby(name, pword):
    global status, players
    running = True

    name_1 = name.lower()

    #check if start is active
    def poll_server_for_start():
        if not network:
            return None
        try:
            reply = network.send(f"{player_id}:-1,-1")
            return reply
        except Exception as e:
            print("Lobby network poll error:", e)
            return None

    while running:
        screen.fill("white")
        mx, my = pygame.mouse.get_pos()
        screen.blit(bg_img, (0, 0))
        draw_text('Lobby', retroFont, (255, 255, 255), screen, 250, 20)

        #get json file & connect it to current game
        data = load_log()

        #loop through the json file to look for the number of players connected to this game
        for i in data:
            if i["host_name"] == name.lower() and i["password"] ==pword:
                players = i.get("players_connected", 1)
                players_connected = players
                game_active = i.get("active", True)
                break

        draw_text(f"Players waiting: {players_connected}/2", retroSmall, (255, 255, 255), screen, 250, 200)


        start_game_b = pygame.Rect(475, 500, 300, 40)
        #HERE ADD button UI right now just ugly red box for testing
        pygame.draw.rect(screen, (255, 0, 0), start_game_b)
        screen.blit(start_g, (475, 500))

        if players_connected < 2:
            draw_text("Waiting for Player", retroSmall, (255,255,255), screen, 250,310)
            pass
        else:
            try:

                if network:
                    network.send("START")
            except Exception as e:
                print("Error sending START to server", e)

            st = poll_server_for_start()
            if st == "START":
                #send initial pos to network after start
                initial_data = f"{player_id}:50,50" if player_id == 0 else f"{player_id}:100,100"
                try:
                    network.send(initial_data)
                except Exception as e:
                    print("Error sending initial pos:", e)

                level = Level(level_map1, screen, player_id=player_id, multiplayer=multiplayer)
                game_state["level"] = level
                game_state["network"] = network
                game_state["player_id"] = player_id
                game_state["multiplayer"] = True
                status = 2
                return

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #button for start game need to check if players >= 2
            if event.type == MOUSEBUTTONDOWN:
                if start_game_b.collidepoint(event.pos):
                    if players_connected < 2:
                        messagebox.showinfo(title='Pixel Chase', message='Not enough players yet!')
                        pass
                    else:
                        try:
                            if network:
                                network.send("START")
                        except Exception as e:
                            print("Error sending START to server", e)

                        st = poll_server_for_start()
                        if st == "START":
                            # messagebox.showinfo(title="Pixel Chase", message="Game starting Now!")
                            level = Level(level_map1, screen, player_id=player_id,multiplayer=multiplayer)
                            game_state["level"] = level
                            game_state["network"] = network
                            game_state["player_id"] = player_id
                            game_state["multiplayer"] = True
                            status = 2
                            return

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    status = 1
                    return


        pygame.display.update()
        clock.tick(fps)

def create_game():
    global status
    running = True
    user_name = ''
    active = False
    # make the texbox
    colour_active = pygame.Color((200, 200, 200))
    colour_passive = pygame.Color((255, 255, 255))
    colour = colour_passive
    input_rect_name = pygame.Rect(500, 250, 340, 62)

    #textbox 2
    user_pword = ''
    active2 = False
    input_rect_pword = pygame.Rect(600, 350, 340, 62)

    while running:
        screen.fill("white")
        mx,my = pygame.mouse.get_pos()
        screen.blit(bg_img, (0, 0))
        draw_text('Create Game', retroFont, (255, 255, 255), screen, 250, 20)
        draw_text('Enter Name: ', retroSmall, (255, 255, 255), screen, 50, 250)
        draw_text('Enter Password: ', retroSmall, (255, 255, 255), screen, 50, 350)
        draw_text('Enter - Continue', retroSmall, (255, 255, 255), screen, 20, 600)
        draw_text('Esc - Back', retroSmall, (255,255,255), screen, 800, 600)

        #make the textbox change colour if pressed
        if active:
            colour_n = colour_active
        else:
            colour_n = colour_passive
        if active2:
            colour_p = colour_active
        else:
            colour_p = colour_passive


        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                #check if mouse presses textboxes
                if input_rect_name.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                if input_rect_pword.collidepoint(event.pos):
                    active2 = True
                else:
                    active2 = False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    status = 1
                    return
                if event.key == K_RETURN:
                    if len(user_name) > 0 and len(user_pword) > 0:
                        success = add_log(user_name, user_pword)
                        if success:
                            messagebox.showinfo(title='Pixel Chase', message='Game Created Successfully!')
                            # create instance of game dictionary
                            lobby_state["username"] = user_name
                            lobby_state["password"] = user_pword

                            status = 7
                            return
                        else:
                            messagebox.showinfo(title='Pixel Chase', message='Cannot make duplicate games!')
                        new_obj = {
                            "host_name": user_name,
                            "password": user_pword,
                            active: True
                        }
                    else:
                        messagebox.showinfo(title='Pixel Chase', message='Invalid Username or Password')

                if active:
                    if event.key == K_BACKSPACE:
                        user_name = user_name[:-1]
                    else:
                        user_name += event.unicode
                if active2:
                    if event.key == K_BACKSPACE:
                        user_pword = user_pword[:-1]
                    else:
                        user_pword += event.unicode
        #Draw the two textboxes
        pygame.draw.rect(screen, colour_n, input_rect_name)
        text_surface = retroSmall.render(user_name, True, (0, 0, 0))
        screen.blit(text_surface, (input_rect_name.x + 5, input_rect_name.y + 5))
        input_rect_name.w = max(100, text_surface.get_width() + 10)

        pygame.draw.rect(screen, colour_p, input_rect_pword)
        text_surface = retroSmall.render(user_pword, True, (0, 0, 0))
        screen.blit(text_surface, (input_rect_pword.x + 5, input_rect_pword.y + 5))
        input_rect_pword.w = max(100, text_surface.get_width() + 10)

        pygame.display.flip()

        pygame.display.update()
        clock.tick(fps)


def join_game():
    global status
    running = True
    user_name = ''
    active = False
    # make the texbox
    colour_active = pygame.Color((200, 200, 200))
    colour_passive = pygame.Color((255, 255, 255))
    colour = colour_passive
    input_rect_name = pygame.Rect(500, 250, 340, 62)

    # textbox 2
    user_pword = ''
    active2 = False
    input_rect_pword = pygame.Rect(600, 350, 350, 62)

    while running:
        screen.fill("white")
        mx, my = pygame.mouse.get_pos()
        screen.blit(bg_img, (0, 0))
        draw_text('Join Game', retroFont, (255, 255, 255), screen, 250, 20)
        draw_text('Enter Name: ', retroSmall, (255, 255, 255), screen, 50, 250)
        draw_text('Enter Game ID: ', retroSmall, (255, 255, 255), screen, 50, 350)
        draw_text('Enter - Continue', retroSmall, (255, 255, 255), screen, 20, 600)
        draw_text('Esc - Back', retroSmall, (255, 255, 255), screen, 800, 600)

        # make the textbox change colour if pressed
        if active:
            colour_n = colour_active
        else:
            colour_n = colour_passive
        if active2:
            colour_p = colour_active
        else:
            colour_p = colour_passive

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # check if mouse presses textboxes
                if input_rect_name.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                if input_rect_pword.collidepoint(event.pos):
                    active2 = True
                else:
                    active2 = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    status = 1
                    return
                if event.key == K_RETURN:
                    if len(user_name) > 0 and len(user_pword) > 0:
                        success = join_game_log(user_name, user_pword)
                        if success:
                            messagebox.showinfo(title='Pixel Chase', message='Game Joined Successfully!')
                            #create instance of game dictionary
                            lobby_state["username"] = user_name
                            lobby_state["password"] = user_pword

                            status = 7
                            return

                        else:
                            messagebox.showinfo(title='Pixel Chase',
                                                message='Invalid Username or Password or Game Full')
                    else:
                        messagebox.showinfo(title='Pixel Chase', message='Invalid Username or Password')

                if active:
                    if event.key == K_BACKSPACE:
                        user_name = user_name[:-1]
                    else:
                        user_name += event.unicode
                if active2:
                    if event.key == K_BACKSPACE:
                        user_pword = user_pword[:-1]
                    else:
                        user_pword += event.unicode
        #Draw the two textboxes
        pygame.draw.rect(screen, colour_n, input_rect_name)
        text_surface = retroSmall.render(user_name, True, (0, 0, 0))
        screen.blit(text_surface, (input_rect_name.x + 5, input_rect_name.y + 5))
        input_rect_name.w = max(100, text_surface.get_width() + 10)

        pygame.draw.rect(screen, colour_p, input_rect_pword)
        text_surface = retroSmall.render(user_pword, True, (0, 0, 0))
        screen.blit(text_surface, (input_rect_pword.x + 5, input_rect_pword.y + 5))
        input_rect_pword.w = max(100, text_surface.get_width() + 10)

        pygame.display.flip()

        pygame.display.update()
        clock.tick(fps)
def settings():
    running = True
    while running:
        screen.fill("white")
        mx, my = pygame.mouse.get_pos()
        screen.blit(bg_img, (0, 0))
        draw_text('Controls', retroFont, (255, 255, 255), screen, 350, 20)

        draw_text('Up Arrow - Jump', retroSmall, (255, 255, 255), screen, 350, 200)
        draw_text('Left  Arrow - Move Left', retroSmall, (255, 255, 255), screen, 200, 350)
        draw_text('Right Arrow - Move Right', retroSmall, (255, 255, 255), screen, 200, 500)
        draw_text('Esc - back', retroSmall, (255,255,255), screen, 400, 600)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        pygame.display.update()
        clock.tick(fps)


def game_over(winner_id, local_id):
    global status

    if winner_id == local_id:
        msg = "You Win!"
    else:
        msg = "Game Over, You Lose!"

    running = True
    while running:
        screen.fill("white")
        #graphics
        screen.blit(bg_img, (0, 0))
        draw_text("Pixel Chase", retroFont, "white", screen, 200,20)
        draw_text(msg, retroSmall, "white", screen, 400,300)

        mx, my = pygame.mouse.get_pos()
        exit_btn = pygame.Rect(475, 500, 400, 60)
        pygame.draw.rect(screen, (0,0,0), exit_btn)
        draw_text("Quit Game", retroSmall, "white", screen, 520, 510)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if exit_btn.collidepoint((mx,my)):
                    pygame.quit()
                    sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    status = 1
                    running = False
        pygame.display.update()
        clock.tick(fps)



#main loop to run everything
while True:

    if status == 1:
        main_menu()
    elif status == 2:
        game(
            game_state["level"],
            game_state["network"],
            game_state["player_id"],
            game_state["multiplayer"]
        )
    elif status == 3:
        game_over(winner_id, game_state["player_id"])
        pass
    elif status == 4:
        create_game()

    elif status == 5:
        join_game()
    elif status == 6:
        settings()
    elif status == 7:
        lobby(
            lobby_state["username"],
            lobby_state["password"]
        )


