import pygame
import os

global game

class Game:
    Frame = None
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("APOLLO | ALPHA")
        self.screen = pygame.display.set_mode((640, 360), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SCALED)
        self.clock = pygame.time.Clock()

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            self.screen.fill("black")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if Frame != None:
                for entity in Frame.Entities:
                    entity.frameUpdate()
                    entity.draw(self.screen)

            pygame.display.flip()

        pygame.quit()

class Frame:
    Entities = []
    
    def __init__(self):
        pass
    
    def createEntity(self, entity):
        self.Entities.append(entity)
        
    def destroyEntity(self, entity):
        self.Entities.remove(entity)

class GameFrame(Frame):
    def __init__(self):
        self.createEntity(Traveler())
        pass
        

class Entity:
    pos = pygame.Vector2(0, 0)
    size = pygame.Vector2(32, 32)
    direction = 0 #radians 0-360
    
    sprite = pygame.sprite.Sprite()
    
    __texture = "assets/sprites/missing.png"
    
    def __init__(self):
        self.sprite.__init__()
        self.setTexture(self.__texture)
        self.sprite.rect = pygame.Rect(self.pos, self.size)
    
    
    def setTexture(self, texture):
        #check if texture path exists
        if texture != None and os.path.exists(texture):
            self.__texture = pygame.image.load(texture)
        else:
            print(f"Texture {texture} does not exist")
            self.__texture = pygame.image.load("assets/sprites/missing.png")
        
        self.sprite.image = self.__texture
        self.sprite.image.convert()
        

    def draw(self, screen):
        #draw sprite with openGL
        screen.blit(self.sprite.image, self.pos)
        
        
    def frameUpdate(self):
        pass
    
    def Destroy(self):
        game.Frame.destroyEntity(self)
        
class Traveler(Entity):
    def __init__(self):
        super().__init__()
        self.setTexture("assets/sprites/traveler.png")
        
    def frameUpdate(self):
        pass
        

game = Game()
game.Frame = GameFrame()
game.run()