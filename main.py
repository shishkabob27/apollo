import pygame
import os
import random
import platform
import asyncio

from macros import * 

global game

class Camera:
    Position = pygame.Vector2(0, 0)
    def __init__(self):
        pass
    
    def frameUpdate(self):
        pass
    
    def PositionCheck(self):
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
    
    CachedFiles = []
    
    def __init__(self):
        pass
    
    def createEntity(self, entity):
        self.Entities.append(entity)
        
    def destroyEntity(self, entity):
        del self.Entities[self.Entities.index(entity)]
        
    def draw(self, screen):
        pass
        
    def frameUpdate(self):
        for entity in Frame.Entities:
            entity.frameUpdate()
            entity.draw(game.screen)
        self.Camera.frameUpdate()
        
class Game:
    Frame = None
    
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(f"{TITLE} | {VERSION} | {platform.system()} {platform.release()}")
        self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SCALED)
        self.clock = pygame.time.Clock()
        print("StellarFuse initialized")

    def run(self):
        self.Frame = LoadingFrame(GameFrame)
        
        running = True
        while running:
            self.clock.tick(FPS)
            self.screen.fill("black")
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

            if self.Frame != None:
                self.Frame.draw(self.screen)
                self.Frame.frameUpdate()
            else:
                print("No frame loaded!")
                
            versionText = pygame.font.SysFont("MS Sans Serif", 18).render(f"Pygame {pygame.ver} | SDL {pygame.SDL.major}.{pygame.SDL.minor}.{pygame.SDL.patch} ", True, "white")
            self.screen.blit(versionText, (0, 0))
            
            fpsText = pygame.font.SysFont("MS Sans Serif", 18).render(f"FPS: {round(self.clock.get_fps())}", True, "white")
            self.screen.blit(fpsText, (0, 16))
            
            print(f"{self.Frame.__class__.__name__}")
            
            pygame.display.flip()

        pygame.quit()
        
    def changeFrame(self, newFrame):
        del self.Frame
        self.Frame = newFrame()
            
class GameFrame(Frame):
    Size = pygame.Vector2(2048, 2048)
    
    CachedFiles = ["assets/sprites/traveler_0.png", "assets/sprites/traveler_1.png", "assets/sprites/traveler_2.png", "assets/sprites/traveler_3.png", "assets/sprites/background_grass.png"]
    
    GrassBackground = pygame.image.load("assets/sprites/background_grass.png")
    
    def __init__(self):
        super().__init__()
        #create 1000 travelers at random positions for testing
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
            
        self.Camera.PositionCheck()
        
    
    def draw(self, screen):
        super().draw(screen)

        #draw background
        for x in range(0, int(self.Size.x), 512):
            for y in range(0, int(self.Size.y), 512):
                screen.blit(self.GrassBackground, (x, y) - self.Camera.Position)
                
class LoadingFrame(Frame):
    newFrame = None
    
    def __init__(self, newFrame):
        super().__init__()
        self.newFrame = newFrame
    
    def frameUpdate(self):
        super().frameUpdate()
        asyncio.run(self.LoadAssets())
        game.changeFrame(self.newFrame)
        
    def draw(self, screen):
        super().draw(screen)
        loadingText = pygame.font.SysFont("MS Sans Serif", 32).render("Loading", True, "white")
        screen.blit(loadingText, (SCREEN_WIDTH / 2 - loadingText.get_width() / 2, SCREEN_HEIGHT / 2 - loadingText.get_height() / 2))

    async def LoadAssets(self):
        if self.newFrame.CachedFiles.__len__() > 0:
            for file in self.newFrame.CachedFiles:
                if os.path.exists(file):
                    if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".gif") or file.endswith(".bmp") or file.endswith(".pcx") or file.endswith(".tga") or file.endswith(".tif") or file.endswith(".lbm") or file.endswith(".pbm") or file.endswith(".pgm") or file.endswith(".ppm") or file.endswith(".xpm"):
                        pygame.image.load(file).convert()
                        print(f"Loaded texture {file}")
                    elif file.endswith(".wav") or file.endswith(".mp3") or file.endswith(".ogg") or file.endswith(".flac"):
                        pygame.mixer.Sound(file)
                        print(f"Loaded sound {file}")
                    elif file.endswith(".ttf") or file.endswith(".otf"):
                        pygame.font.Font(file)
                        print(f"Loaded font {file}")
                else:
                    print(f"File {file} does not exist!")

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
        
        self.sprite.image = pygame.image.load(self.texture).convert()

    def draw(self, screen):
        if self.Visible:
            if self.Position.x + self.Size.x > game.Frame.Camera.Position.x and self.Position.x < game.Frame.Camera.Position.x + SCREEN_WIDTH and self.Position.y + self.Size.y > game.Frame.Camera.Position.y and self.Position.y < game.Frame.Camera.Position.y + SCREEN_HEIGHT:
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
game.run()