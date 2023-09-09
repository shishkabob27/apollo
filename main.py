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
        
class Frame:
    Entities = []
    Camera = Camera()
    
    def __init__(self):
        pass
    
    def createEntity(self, entity):
        self.Entities.append(entity)
        
    def destroyEntity(self, entity):
        self.Entities.remove(entity)
        
    def frameUpdate(self):
        for entity in Frame.Entities:
            entity.frameUpdate()
            entity.draw(game.screen)

class GameFrame(Frame):
    def __init__(self):
        super().__init__()
        self.createEntity(Traveler())
        pass
        
    def frameUpdate(self):
        super().frameUpdate()
        if pygame.key.get_pressed()[pygame.K_w]:
            self.Camera.Position.y -= 1
        if pygame.key.get_pressed()[pygame.K_s]:
            self.Camera.Position.y += 1
        if pygame.key.get_pressed()[pygame.K_a]:
            self.Camera.Position.x -= 1
        if pygame.key.get_pressed()[pygame.K_d]:
            self.Camera.Position.x += 1

class Entity:
    Position = pygame.Vector2(0, 0)
    Size = pygame.Vector2(32, 32)
    Direction = 0 #0 = up, 1 = right, 2 = down, 3 = left
    
    Visible = True
    
    sprite = pygame.sprite.Sprite()
    
    texture = "assets/sprites/missing.png" # Should not be used directly (use setTexture)
    
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
            print(f"Texture {newtexture} does not exist")
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