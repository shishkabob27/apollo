import pygame
import os
import random

from macros import * 

global game

class Game:
    Frame = None
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(f"{TITLE} | {VERSION}")
        self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SCALED)
        self.clock = pygame.time.Clock()
        print("StellarFuse initialized")

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            self.screen.fill("black")
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

            if self.Frame != None:
                self.Frame.frameUpdate()

            pygame.display.flip()

        pygame.quit()

class Camera:
    Position = pygame.Vector2(0, 0)
    def __init__(self):
        pass
    
    def frameUpdate(self):
        #check if camera is out of bounds
        if self.Position.x < 0:
            self.Position.x = 0
        if self.Position.y < 0:
            self.Position.y = 0
        if self.Position.x > game.Frame.Size.x - SCREEN_WIDTH:
            self.Position.x = game.Frame.Size.x - SCREEN_WIDTH
        if self.Position.y > game.Frame.Size.y - SCREEN_HEIGHT:
            self.Position.y = game.Frame.Size.y - SCREEN_HEIGHT

class Frame:
    Entities = []
    Size = pygame.Vector2(SCREEN_WIDTH, SCREEN_HEIGHT)
    Camera = Camera()
    
    def __init__(self):
        pass
    
    def createEntity(self, entity):
        self.Entities.append(entity)
        
    def destroyEntity(self, entity):
        self.Entities.remove(entity)
        
    def frameUpdate(self):
        self.Camera.frameUpdate()
        for entity in Frame.Entities:
            entity.frameUpdate()
            entity.draw(game.screen)

class GameFrame(Frame):
    Size = pygame.Vector2(2048, 2048)
    
    def __init__(self):
        super().__init__()
        #create 50 travelers at random positions for testing
        for i in range(1000):
            traveler = Traveler()
            traveler.Position = pygame.Vector2(random.randint(0, self.Size.x), random.randint(0, self.Size.y))
            self.createEntity(traveler)
        pass
        
    def frameUpdate(self):
        super().frameUpdate()
        if pygame.key.get_pressed()[pygame.K_w]:
            self.Camera.Position.y -= 4
        if pygame.key.get_pressed()[pygame.K_s]:
            self.Camera.Position.y += 4
        if pygame.key.get_pressed()[pygame.K_a]:
            self.Camera.Position.x -= 4
        if pygame.key.get_pressed()[pygame.K_d]:
            self.Camera.Position.x += 4

class Entity:
    Position = pygame.Vector2(0, 0)
    Size = pygame.Vector2(32, 32)
    Direction = 0 #0 = up, 1 = right, 2 = down, 3 = left
    
    #if false, entity will not be drawn
    Visible = True
    
    sprite = pygame.sprite.Sprite()
    
    texture = "assets/sprites/missing.png" # Should not be set directly (use setTexture)
    
    def __init__(self):
        self.sprite.__init__()
        self.setTexture(self.texture)
        self.sprite.rect = pygame.Rect(self.Position, self.Size)
        self.Direction = 2 #default direction is down
    
    
    def setTexture(self, newtexture):
        #check if texture path exists
        if newtexture != None and os.path.exists(newtexture):
            self.texture = newtexture
        else:
            print(f"Texture {newtexture} does not exist!")
            self.texture = "assets/sprites/missing.png"
        
        self.sprite.image = pygame.image.load(self.texture)
        self.sprite.image.convert()

    def draw(self, screen):
        if self.Visible:
            screen.blit(self.sprite.image, self.Position - game.Frame.Camera.Position)
        
    def frameUpdate(self):
        pass
    
    def Destroy(self):
        game.Frame.destroyEntity(self)
        
class Traveler(Entity):
    def __init__(self):
        super().__init__()
        
    def frameUpdate(self):
        super().frameUpdate()
            
        directionImage = f"assets/sprites/traveler_{self.Direction}.png"
        if self.texture != directionImage:
            self.setTexture(directionImage)
        

game = Game()
game.Frame = GameFrame()
game.run()