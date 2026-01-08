from os import walk
import pygame

def import_folder(path):

    surface_list = []
    for _,__, img_files in walk (path):
        for file in img_files:
            full_path = path + "/" + file
            image = pygame.image.load(full_path)
            image = pygame.transform.scale(image, (60, 60))
            #pygame.transform.flip(image, True, False)
            surface_list.append(image)
    return surface_list