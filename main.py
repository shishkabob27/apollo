import pygame
import pygame_gui
import os
import sys
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
        self.createGUI()
        pass
    
    def createEntity(self, entity):
        self.Entities.append(entity)
        #sort entities by draw layer
        self.Entities.sort(key=lambda x: x.DrawOrder)
        
    def destroyEntity(self, entity):
        del self.Entities[self.Entities.index(entity)]
        
    def createGUI(self):
        pass
    
    def updateGUI(self):
        pass
    
    def GUIButtonPressed(self, button):
        pass
        
    def draw(self, screen):
        pass
        
    def frameUpdate(self):
        for entity in self.Entities:
            entity.frameUpdate()
            entity.draw(game.screen)
        self.Camera.frameUpdate()
        
class Game:
    Frame = None
    dt = 0
    
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        if DEBUG:
            pygame.display.set_caption(f"{TITLE} | {VERSION} | {platform.system()} {platform.release()}")
        else:
            pygame.display.set_caption(f"{TITLE} | {VERSION}")
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.guimanager = pygame_gui.UIManager(SCREEN_SIZE, "assets/theme.json")
        
        print("StellarFuse initialized")

    def run(self):
        self.Frame = LoadingFrame(GameFrame)
        
        running = True
        while running:
            self.clock.tick(FPS)
            self.dt = self.clock.get_time() / 1000
            self.screen.fill("black")
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                    
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.Frame.GUIButtonPressed(event.ui_element)
                self.guimanager.process_events(event)
            
            if self.Frame != None:
                self.Frame.draw(self.screen)
                self.Frame.frameUpdate()
                self.Frame.updateGUI()
            else:
                print("No frame loaded!")
                
            fpstext = pygame.font.SysFont("microsoftsansserif", 16).render(f"{round(self.clock.get_fps())}", False, "white")
            self.screen.blit(fpstext, (0, 0))
            
            self.guimanager.update(self.dt)
            self.guimanager.draw_ui(self.screen)
            
            pygame.display.flip()

        pygame.quit()
        
    def changeFrame(self, newFrame):
        del self.Frame
        self.Frame = newFrame()
            
class GameFrame(Frame):
    Size = pygame.Vector2(2048, 2048)
    
    CachedFiles = ["assets/sprites/traveler_0.png",
                   "assets/sprites/traveler_1.png",
                   "assets/sprites/traveler_2.png",
                   "assets/sprites/traveler_3.png",
                   "assets/sprites/background_grass.png",
                   "assets/sprites/select_build.png",
                   "assets/sprites/select_destroy.png",
                   "assets/sprites/tiles/wall.png",
                   "assets/sprites/tiles/floor.png"]
    
    GrassBackground = pygame.image.load("assets/sprites/background_grass.png")
    SelectBuildImage = pygame.image.load("assets/sprites/select_build.png")
    SelectDestroyImage = pygame.image.load("assets/sprites/select_destroy.png")
    
    Mode = "interact" #interact, build, destroy
    InSpace = False
    Money = 100000
    
    SelectedTile = None
    
    def __init__(self):
        super().__init__()
        #create 100 travelers at random positions for testing
        for i in range(100):
            traveler = Traveler()
            traveler.Position = pygame.Vector2(random.randint(0, self.Size.x), random.randint(0, self.Size.y))
            self.createEntity(traveler)
        pass
        
    def frameUpdate(self):
        super().frameUpdate()
        
        cameraspeed = 4
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            cameraspeed = 8
        
        if pygame.key.get_pressed()[pygame.K_w]:
            self.Camera.Position.y -= cameraspeed
        if pygame.key.get_pressed()[pygame.K_s]:
            self.Camera.Position.y += cameraspeed
        if pygame.key.get_pressed()[pygame.K_a]:
            self.Camera.Position.x -= cameraspeed
        if pygame.key.get_pressed()[pygame.K_d]:
            self.Camera.Position.x += cameraspeed
            
        self.Camera.PositionCheck()
        
        if pygame.key.get_pressed()[pygame.K_1]:
            self.SetMode("interact")
        if pygame.key.get_pressed()[pygame.K_2]:
            self.SetMode("build")
        if pygame.key.get_pressed()[pygame.K_3]:
            self.SetMode("destroy")
            
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            #move all travelers to mouse position
            for entity in self.Entities:
                if isinstance(entity, Traveler):
                    entity.MoveToDestination(pygame.Vector2(pygame.mouse.get_pos()[0] + self.Camera.Position.x, pygame.mouse.get_pos()[1] + self.Camera.Position.y))

        #draw interact selection box
        #align to 32x32 grid
        mousepos = pygame.Vector2(pygame.mouse.get_pos()[0] + self.Camera.Position.x, pygame.mouse.get_pos()[1] + self.Camera.Position.y)
        mousepos.x -= mousepos.x % 32
        mousepos.y -= mousepos.y % 32
        
        if self.Mode != "interact":
            SelectImage = None
            if self.Mode == "build":
                SelectImage = self.SelectBuildImage
            elif self.Mode == "destroy":
                SelectImage = self.SelectDestroyImage
            
            game.screen.blit(SelectImage, mousepos - self.Camera.Position)
        
        #check if mouse isnt on gui
        if pygame.mouse.get_pressed()[0] and not game.guimanager.get_hovering_any_element():
             #if left mouse button is pressed
            if self.Mode == "build" and self.SelectedTile != None:
                if self.Money >= Tile.Cost:
                    #check if tile is occupied
                    tileOccupied = False
                    for entity in self.Entities:
                        if isinstance(entity, Tile):
                            if entity.Position == mousepos:
                                tileOccupied = True
                                break
                        if isinstance(entity, Traveler):
                            #check traveler size because travelers are not locked in a grid
                            if self.SelectedTile.Collidable and entity.Position.x + entity.Size.x > mousepos.x and entity.Position.x < mousepos.x + self.SelectedTile.Size.x and entity.Position.y + entity.Size.y > mousepos.y and entity.Position.y < mousepos.y + self.SelectedTile.Size.y:
                                tileOccupied = True
                                break
                    if not tileOccupied:
                        #create tile at mouse position
                        tile = self.SelectedTile()
                        tile.Position = mousepos
                        self.createEntity(tile)
                        self.RemoveMoney(Tile.Cost)
            elif self.Mode == "destroy":
                #check if tile is occupied
                tileOccupied = False
                for entity in self.Entities:
                    if entity.Position == mousepos:
                        tileOccupied = True
                        break
                if tileOccupied:
                    #destroy tile at mouse position
                    for entity in self.Entities:
                        if entity.Position == mousepos:
                            entity.Destroy()
                            self.AddMoney(Tile.Cost * 0.5)
                            break
        
    def AddMoney(self, amount):
        self.Money += amount
    
    def RemoveMoney(self, amount):
        self.Money -= amount

    def createGUI(self):
        super().createGUI()
        self.gui_sidebar = pygame_gui.elements.UIWindow(pygame.Rect((2, 2), (196, SCREEN_HEIGHT-24)), game.guimanager, "Ship", resizable=True)
        self.gui_sidebar_interact_travelerstext = pygame_gui.elements.UILabel(pygame.Rect((4, 0), (196, 22)), "Travelers", game.guimanager, self.gui_sidebar)
        
        self.gui_bottombar = pygame_gui.elements.UIPanel(pygame.Rect((0, SCREEN_HEIGHT - 20), (SCREEN_WIDTH, 20)), 0, game.guimanager)
        
        self.gui_moneytext = pygame_gui.elements.UILabel(pygame.Rect((2, 0), (96, 18)), f"${self.Money}", game.guimanager, self.gui_bottombar)
        
        self.gui_bottombar_interact = pygame_gui.elements.UIButton(pygame.Rect((SCREEN_WIDTH - 288, 0), (94, 18)), "Interact", game.guimanager, self.gui_bottombar)
        self.gui_bottombar_build = pygame_gui.elements.UIButton(pygame.Rect((SCREEN_WIDTH - 192, 0), (94, 18)), "Build", game.guimanager, self.gui_bottombar)
        self.gui_bottombar_destroy = pygame_gui.elements.UIButton(pygame.Rect((SCREEN_WIDTH - 96, 0), (94, 18)), "Destroy", game.guimanager, self.gui_bottombar)
        
        #create button for each tile
        self.tilebuttons = []
        button_offset = 2
        for tile in Tile.__subclasses__():
            self.tilebuttons.append(pygame_gui.elements.UIButton(pygame.Rect((2, button_offset), (96, 16)), tile.Name, game.guimanager, self.gui_sidebar))
            button_offset += 18
        
    def updateGUI(self):
        super().updateGUI()
        #get count of entities of type Traveler
        travnum = 0
        for entity in self.Entities:
            if isinstance(entity, Traveler):
                travnum += 1
        
        if self.Mode == "interact":
            #set sidebar text
            self.gui_sidebar.title_bar.set_text("Ship")
            self.gui_sidebar_interact_travelerstext.set_text(f"Travelers: {travnum}")
            self.gui_sidebar_interact_travelerstext.show()
        else:
            self.gui_sidebar_interact_travelerstext.hide()
      
        if self.Mode == "build":
            self.gui_sidebar.title_bar.set_text("Build")
            
            for button in self.tilebuttons:
                button.show()
        else:
            for button in self.tilebuttons:
                button.hide()
            
        if self.Mode == "destroy":
            self.gui_sidebar.hide()
        else:
            self.gui_sidebar.show()
            
        
        
        self.gui_moneytext.set_text(f"${self.Money:.0f}")
        
    def SetMode(self, mode):
        self.Mode = mode
        
    def GUIButtonPressed(self, button):
        super().GUIButtonPressed(button)
        
        if button == self.gui_bottombar_interact:
            self.SetMode("interact")
            return
        elif button == self.gui_bottombar_build:
            self.SetMode("build")
            return
        elif button == self.gui_bottombar_destroy:
            self.SetMode("destroy")
            return
            
        #check if button is a tile button
        for tile in Tile.__subclasses__():
            if button.text == tile.Name:
                self.SelectedTile = tile
                return
    
    def draw(self, screen):
        super().draw(screen)

        #draw background
        if self.InSpace == False:
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
        game.guimanager.clear_and_reset()
        asyncio.run(self.LoadAssets())
        game.changeFrame(self.newFrame)
        
    def draw(self, screen):
        super().draw(screen)
        loadingText = pygame.font.SysFont("microsoftsansserif", 32).render("Loading", False, "white")
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
                    
class MainMenuFrame(Frame):
    def __init__(self):
        super().__init__()
        pass
    
    def frameUpdate(self):
        super().frameUpdate()
        pass
    
    
    def createGUI(self):
        super().createGUI()
        self.gui_title = pygame_gui.elements.UILabel(pygame.Rect((SCREEN_WIDTH - 64, 0), (64, 32)), f"{TITLE}", game.guimanager)
        self.gui_playbutton = pygame_gui.elements.UIButton(pygame.Rect((2, SCREEN_HEIGHT- 52), (96, 24)), "Play", game.guimanager)
        self.gui_quitbutton = pygame_gui.elements.UIButton(pygame.Rect((2, SCREEN_HEIGHT- 26), (96, 24)), "Quit", game.guimanager)
        
    def GUIButtonPressed(self, button):
        super().GUIButtonPressed(button)
        
        if button == self.gui_playbutton:
            game.Frame = LoadingFrame(GameFrame)
        elif button == self.gui_quitbutton:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        
        

class Entity:
    Health = 100
    Position = pygame.Vector2(0, 0)
    Size = pygame.Vector2(32, 32)
    Direction = 0 #0 = up, 1 = right, 2 = down, 3 = left
    
    DrawOrder = 0
    
    LockedInBounds = True #if true, entity cannot move out of bounds
    
    Collidable = True #if true, entity will collide with other entities
    
    Visible = True #if false, entity will not be drawn
    
    sprite = None
    
    texture = "assets/sprites/missing.png" # Should not be set directly (use setTexture)
    
    def __init__(self):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.__init__()
        self.sprite.image = pygame.image.load("assets/sprites/missing.png").convert()
        self.sprite.rect = pygame.Rect(self.Position, self.Size)
        self.Direction = 2 #default direction is down
    
    
    def setTexture(self, newtexture):
        if newtexture == self.texture:
            return
        
        try:
            self.sprite.image = pygame.image.load(newtexture).convert()
            self.texture = newtexture
        except:
            print(f"Texture {self.texture} does not exist!")
            self.texture = "assets/sprites/missing.png"
            self.sprite.image = pygame.image.load(self.texture).convert()

    def draw(self, screen):
        if self.Visible:
            if self.Position.x + self.Size.x > game.Frame.Camera.Position.x and self.Position.x < game.Frame.Camera.Position.x + SCREEN_WIDTH and self.Position.y + self.Size.y > game.Frame.Camera.Position.y and self.Position.y < game.Frame.Camera.Position.y + SCREEN_HEIGHT:
                screen.blit(self.sprite.image, self.Position - game.Frame.Camera.Position)
        
    def frameUpdate(self):
        if self.LockedInBounds:
            if self.Position.x < 0:
                self.Position.x = 0
            if self.Position.y < 0:
                self.Position.y = 0
            if self.Position.x > game.Frame.Size.x - self.Size.x:
                self.Position.x = game.Frame.Size.x - self.Size.x
            if self.Position.y > game.Frame.Size.y - self.Size.y:
                self.Position.y = game.Frame.Size.y - self.Size.y
        pass
    
    def Destroy(self):
        game.Frame.destroyEntity(self)

class Tile(Entity):
    DrawOrder = 0
    
    Name = "Base Tile"
    Layer = 0
    Cost = 500
        
class Wall(Tile):
    Name = "Wall"
    Layer = 1
    Cost = 500
    
    def __init__(self):
        super().__init__()
        self.setTexture("assets/sprites/tiles/wall.png")

class Floor(Tile):
    Name = "Floor"
    Layer = 0
    Cost = 100
    Collidable = False
    
    def __init__(self):
        super().__init__()
        self.setTexture("assets/sprites/tiles/floor.png")
    
    
class Traveler(Entity):
    DrawOrder = 2
    Collidable = False
    
    ai_state = 1 #0 = stopped, 1 = wandering, 2 = moving to destination
    destinationPosition = pygame.Vector2(0, 0)
    
    def __init__(self):
        super().__init__()
        
    def frameUpdate(self):
        super().frameUpdate()
        
        if self.ai_state == 1:
            self.Wander()
        elif self.ai_state == 2:
            if self.Position == self.destinationPosition:
                self.ai_state = 0
                
            if self.Position.x < self.destinationPosition.x:
                self.Direction = 1
            elif self.Position.x > self.destinationPosition.x:
                self.Direction = 3
            elif self.Position.y < self.destinationPosition.y:
                self.Direction = 2
            elif self.Position.y > self.destinationPosition.y:
                self.Direction = 0
            self.Move()
            
        elif self.ai_state == 0:
            self.ai_state = 1
        
            
        directionImage = f"assets/sprites/traveler_{self.Direction}.png"
        #if self.texture != directionImage:
        self.setTexture(directionImage)
            
    def MoveToDestination(self, destination):
        if self.ai_state != 2:
            self.ai_state = 2
            self.destinationPosition = destination
        pass
    
    def Wander(self):
        if random.randint(0, 10) == 0:
            self.Direction = random.randint(0, 3)
            
        self.Move()
            
    def Move(self):
        if self.Direction == 0:
            self.Position.y -= 1
        elif self.Direction == 1:
            self.Position.x += 1
        elif self.Direction == 2:
            self.Position.y += 1
        elif self.Direction == 3:
            self.Position.x -= 1
            
        #make sure traveler is not colliding with any other entities
        for entity in game.Frame.Entities:
            if entity.Collidable and entity != self:
                if self.Position.x + self.Size.x > entity.Position.x and self.Position.x < entity.Position.x + entity.Size.x and self.Position.y + self.Size.y > entity.Position.y and self.Position.y < entity.Position.y + entity.Size.y:
                    #traveler is colliding with entity
                    #move traveler back so they are not colliding
                    if self.Direction == 0:
                        self.Position.y += 1
                    elif self.Direction == 1:
                        self.Position.x -= 1
                    elif self.Direction == 2:
                        self.Position.y -= 1
                    elif self.Direction == 3:
                        self.Position.x += 1
                        
                    break

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
    
game = Game()
game.run()