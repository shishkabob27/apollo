import pygame
import pygame_gui
import os
import sys
import random
import platform
import asyncio
import json
import time

from discordrp import Presence

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
        
    def Tick(self):
        pass
        
    #called when frame is changed
    def endFrame(self):
        pass
    
    #called when game is closed with the frame active
    def endGame(self):
        pass
        
class Game:
    Frame = None
    dt = 0
    
    timesincelasttick = 0
    unixtimewhenframestarted = int(time.time())
    timesincerichpresenceupdate = 10
    
    gui_console = None
    
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
        self.Frame = LoadingFrame(MainMenuFrame)
        
        if not DEBUG:
            self.discordrpc = Presence("1150522780429848716")
        
        running = True
        while running:
            self.clock.tick(FPS)
            self.dt = self.clock.get_time() / 1000
            self.screen.fill("black")
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    if self.Frame != None:
                        self.Frame.endFrame()
                        self.Frame.endGame()
                    running = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                    #destroy or create console gui
                    if self.gui_console != None:
                        self.gui_console.kill()
                        self.gui_console = None
                    else:
                        self.gui_console =  pygame_gui.windows.UIConsoleWindow(rect=pygame.rect.Rect((SCREEN_WIDTH-360, 0), (360, 240)), manager=self.guimanager)
                    
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.Frame.GUIButtonPressed(event.ui_element)
                elif event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED and event.ui_element == self.gui_console:
                    self.ConsoleCommand(event.command)
                    
                self.guimanager.process_events(event)
            
            if self.Frame != None:
                self.Frame.draw(self.screen)
                self.Frame.frameUpdate()
                self.Frame.updateGUI()
            else:
                print("No frame loaded!")
                
            if DEBUG:
                fpstext = pygame.font.SysFont("microsoftsansserif", 16).render(f"{round(self.clock.get_fps())}", False, "white")
                self.screen.blit(fpstext, (0, 0))
            
            self.guimanager.update(self.dt)
            self.guimanager.draw_ui(self.screen)
            
            #Tick
            self.timesincelasttick += self.clock.get_time() / 1000
            if self.timesincelasttick >= 1 / TICKRATE:
                self.timesincelasttick -= 1 / TICKRATE
                self.Frame.Tick()
                for entity in self.Frame.Entities:
                    entity.Tick()    
            
            pygame.display.flip()
            
            #Discord Rich Presence
            self.timesincerichpresenceupdate += self.clock.get_time() / 1000
            if self.timesincerichpresenceupdate >= 10 and DEBUG == False:
                self.timesincerichpresenceupdate = 0
                if self.Frame.__class__ == MainMenuFrame:
                    self.discordrpc.set(
                        {
                            "state": "In Menu",
                            "details": "Main Menu",
                            "assets": {
                                "large_image": "apollo_icon_alt"
                            }
                        }
                    )
                elif self.Frame.__class__ == CharacterCreatorFrame:
                    self.discordrpc.set(
                        {
                            "state": "In Menu",
                            "details": "Character Creator",
                            "assets": {
                                "large_image": "apollo_icon_alt"
                            },
                            "timestamps": {
                                "start": self.unixtimewhenframestarted
                            }
                        }
                    )
                elif self.Frame.__class__ == GameFrame:
                    self.discordrpc.set(
                        {
                            "state": "In Game",
                            "details": "Building ship",
                            "assets": {
                                "large_image": "apollo_icon_alt"
                            },
                            "timestamps": {
                                "start": self.unixtimewhenframestarted
                            }
                        }
                    )

        pygame.quit()
        
    def changeFrame(self, newFrame):
        self.Frame.endFrame()
        del self.Frame
        self.Frame = LoadingFrame(newFrame)
        self.unixtimewhenframestarted = int(time.time())
        
    def ConsoleCommand(self, command):
        args = command.lower().split(" ")
        
        if args[0] == "help":
            game.gui_console.add_output_line_to_log("Commands:")
            game.gui_console.add_output_line_to_log("help - shows this help message")
            game.gui_console.add_output_line_to_log("clear - clears the console")
            game.gui_console.add_output_line_to_log("exit - exits the game")
            game.gui_console.add_output_line_to_log("changeframe <frame> - changes the level")
            game.gui_console.add_output_line_to_log("setmoney <amount> - sets the player's money")
            game.gui_console.add_output_line_to_log("addmoney <amount> - adds money to the player's money")
            game.gui_console.add_output_line_to_log("removemoney <amount> - removes money from the player's money")
            game.gui_console.add_output_line_to_log("setmode <mode> - sets the player's mode")
            game.gui_console.add_output_line_to_log("setticks <ticks> - sets the ticks")
            game.gui_console.add_output_line_to_log("setdifficulty <difficulty> - sets the difficulty")
            game.gui_console.add_output_line_to_log("setinspace <true/false> - sets if the player is in space")
            game.gui_console.add_output_line_to_log("setcamera <x> <y> - sets the camera position")
        elif args[0] == "clear":
            self.gui_console.clear_log()
        elif args[0] == "exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif args[0] == "changeframe":
            if args.__len__() < 2:
                game.gui_console.add_output_line_to_log("Error: Missing argument")
                return
            
            for frame in Frame.__subclasses__():
                if frame.__name__.lower() == args[1]:
                    game.Frame = LoadingFrame(frame)
                    return
            game.gui_console.add_output_line_to_log("Error: Unknown frame")
        elif args[0] == "setmoney":
            if args.__len__() < 2:
                game.gui_console.add_output_line_to_log("Error: Missing argument")
                return
            
            if args[1].isnumeric() == False:
                game.gui_console.add_output_line_to_log(f"Error: Argument is not a number")
                return
                
            if game.Frame.__class__ == GameFrame:
                game.Frame.Money = int(args[1])
            else:
                game.gui_console.add_output_line_to_log("Error: Frame is not GameFrame")
        elif args[0] == "addmoney":
            if args.__len__() < 2:
                game.gui_console.add_output_line_to_log("Error: Missing argument")
                return
            
            if args[1].isnumeric() == False:
                game.gui_console.add_output_line_to_log(f"Error: Argument is not a number")
                return
                
            if game.Frame.__class__ == GameFrame:
                game.Frame.Money += int(args[1])
            else:
                game.gui_console.add_output_line_to_log("Error: Frame is not GameFrame")
        elif args[0] == "removemoney":
            if args.__len__() < 2:
                game.gui_console.add_output_line_to_log("Error: Missing argument")
                return
            
            if args[1].isnumeric() == False:
                game.gui_console.add_output_line_to_log(f"Error: Argument is not a number")
                return
                
            if game.Frame.__class__ == GameFrame:
                game.Frame.Money -= int(args[1])
            else:
                game.gui_console.add_output_line_to_log("Error: Frame is not GameFrame")
        elif args[0] == "setmode":
            if args.__len__() < 2:
                game.gui_console.add_output_line_to_log("Error: Missing argument")
                return
                
            if game.Frame.__class__ == GameFrame:
                game.Frame.SetMode(args[1])
            else:
                game.gui_console.add_output_line_to_log("Error: Frame is not GameFrame")
                
        elif args[0] == "setticks":
            if args.__len__() < 2:
                game.gui_console.add_output_line_to_log("Error: Missing argument")
                return
            
            if args[1].isnumeric() == False:
                game.gui_console.add_output_line_to_log(f"Error: Argument is not a number")
                return
                
            if game.Frame.__class__ == GameFrame:
                game.Frame.TickCount = int(args[1])
            else:
                game.gui_console.add_output_line_to_log("Error: Frame is not GameFrame")
        elif args[0] == "setdifficulty":
            if args.__len__() < 2:
                game.gui_console.add_output_line_to_log("Error: Missing argument")
                return
            
            if args[1].isnumeric() == False:
                game.gui_console.add_output_line_to_log(f"Error: Argument is not a number")
                return
                
            if game.Frame.__class__ == GameFrame:
                game.Frame.Difficulty = int(args[1])
            else:
                game.gui_console.add_output_line_to_log("Error: Frame is not GameFrame")
        elif args[0] == "setinspace":
            if args.__len__() < 2:
                game.gui_console.add_output_line_to_log("Error: Missing argument")
                return
                
            if args[1] == "true":
                if game.Frame.__class__ == GameFrame:
                    game.Frame.InSpace = True
                else:
                    game.gui_console.add_output_line_to_log("Error: Frame is not GameFrame")
            elif args[1] == "false":
                if game.Frame.__class__ == GameFrame:
                    game.Frame.InSpace = False
                else:
                    game.gui_console.add_output_line_to_log("Error: Frame is not GameFrame")
            else:
                game.gui_console.add_output_line_to_log("Error: Argument is not true or false")
        elif args[0] == "setcamera":
            if args.__len__() < 3:
                game.gui_console.add_output_line_to_log("Error: Missing argument")
                return
            
            if args[1].isnumeric() == False or args[2].isnumeric() == False:
                game.gui_console.add_output_line_to_log(f"Error: Argument is not a number")
                return
                
            if game.Frame.__class__ == GameFrame:
                game.Frame.Camera.Position = pygame.Vector2(int(args[1]), int(args[2]))
            else:
                game.gui_console.add_output_line_to_log("Error: Frame is not GameFrame")
        else:
            game.gui_console.add_output_line_to_log("Unknown command")
        
        
class Save:
    
    path = f"save/{TITLE}.sfsave"
    
    data = {
        "difficulty": 1,
        "time": 0,
        "ticks": 0,
        "money": 100000,
        "inSpace": False,
        "camera":{
            "x": 1024 - SCREEN_WIDTH/2,
            "y": 1024 - SCREEN_HEIGHT/2
        },
        "travelers":[],
        "tiles": []
    }
    
    def __init__(self):
        if os.path.exists(self.path) == False:
            self.save()
            
        self.load()
    
    def save(self):
        with open(self.path, "w") as savefile:
            print("Saving...")
            savefile.write(json.dumps(self.data, indent=4))
            savefile.close()
    
    def load(self):
        with open(self.path, "r") as savefile:
            print("Loading...")
            self.data = json.loads(savefile.read())
            savefile.close()
    

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
    Difficulty = 1
    
    TickCount = 0
    
    SelectedTile = None
    
    def __init__(self):
        super().__init__()
        self.save = Save()
        self.LoadSave()
            
    def LoadSave(self):    
        self.Money = self.save.data["money"]
        self.InSpace = self.save.data["inSpace"]
        self.Difficulty = self.save.data["difficulty"]
        self.TickCount = self.save.data["ticks"]
        self.Camera.Position = pygame.Vector2(self.save.data["camera"]["x"], self.save.data["camera"]["y"])
        
        #Travelers
        for traveler in self.save.data["travelers"]:
            newtraveler = Traveler()
            newtraveler.Position = pygame.Vector2(traveler["x"], traveler["y"])
            newtraveler.firstname = traveler["firstname"]
            newtraveler.lastname = traveler["lastname"]
            newtraveler.skincolor = (int(traveler["skincolor"]["r"]), int(traveler["skincolor"]["g"]), int(traveler["skincolor"]["b"]))
            self.createEntity(newtraveler)
            
        #Tiles
        for tile in self.save.data["tiles"]:
            newtile = None
            for tileclass in Tile.__subclasses__():
                if tileclass.__name__ == tile["type"]:
                    newtile = tileclass()
                    break
            if newtile != None:
                newtile.Position = pygame.Vector2(tile["x"], tile["y"])
                self.createEntity(newtile)
                
            
        
    def endFrame(self):
        super().endFrame()
        self.save.data["money"] = self.Money
        self.save.data["inSpace"] = self.InSpace
        self.save.data["ticks"] = self.TickCount
        self.save.data["time"] = round(self.save.data["time"], 2)
        
        #Camera
        self.save.data["camera"] = {
            "x": self.Camera.Position.x,
            "y": self.Camera.Position.y
        }
        
        #Travelers
        self.save.data["travelers"] = []
        for entity in self.Entities:
            if isinstance(entity, Traveler):
                self.save.data["travelers"].append(
                    {
                        "x": entity.Position.x,
                        "y": entity.Position.y,
                        "firstname": entity.firstname,
                        "lastname": entity.lastname,
                        "skincolor": {
                            "r": entity.skincolor[0],
                            "g": entity.skincolor[1],
                            "b": entity.skincolor[2]
                        }
                    })
                
        #Tiles
        self.save.data["tiles"] = []
        for entity in self.Entities:
            if isinstance(entity, Tile):
                self.save.data["tiles"].append(
                    {
                        "type": f"{entity.__class__.__name__}",
                        "x": entity.Position.x,
                        "y": entity.Position.y
                    })
        
        self.save.save()
        
    def frameUpdate(self):
        super().frameUpdate()
        
        self.save.data["time"] += game.dt
        
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
                for entity in self.Entities:
                    if entity.Position == mousepos:
                        if isinstance(entity, Tile):
                            entity.Destroy()
                            self.AddMoney(Tile.Cost * 0.5)
    
    def Tick(self):
        super().Tick()
        self.TickCount += 1
        
        if self.TickCount % 300 == 0 and self.InSpace == False:
            self.AddMoney(10000)
            pygame.mixer.Sound("assets/sounds/cash.mp3").play().set_volume(0.1)
        
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

class CharacterCreatorFrame(Frame):

    def __init__(self):
        super().__init__()
        self.save = Save()
        self.RandomizeTraveler()
        pass
    
    def frameUpdate(self):
        super().frameUpdate()
        pass
    
    def createGUI(self):
        super().createGUI()
        self.page = 1
        
        self.gui_creatorwindow = pygame_gui.elements.UIWindow(pygame.Rect((SCREEN_WIDTH / 2 - 128, SCREEN_HEIGHT / 2 - 160), (256, 320)), game.guimanager, "Character Creator", resizable=False, draggable=False)
        
        #back and next buttons
        self.gui_backbutton = pygame_gui.elements.UIButton(pygame.Rect((0, 276), (128, 24)), "Back", game.guimanager, self.gui_creatorwindow)
        self.gui_nextbutton = pygame_gui.elements.UIButton(pygame.Rect((128, 276), (128, 24)), "Next", game.guimanager, self.gui_creatorwindow)
        
        self.gui_s1 = []
        
        self.gui_s1_difficultytext = pygame_gui.elements.UILabel(pygame.Rect((4, 0), (256, 22)), "Difficulty", game.guimanager, self.gui_creatorwindow)
        self.gui_s1_difficulty = pygame_gui.elements.UIDropDownMenu(["Easy", "Normal", "Hard"], "Easy", pygame.Rect((0, 24), (254, 22)), game.guimanager, self.gui_creatorwindow)
        
        self.gui_s1.append(self.gui_s1_difficultytext)
        self.gui_s1.append(self.gui_s1_difficulty)    
        
        self.gui_s2 = []
        
        #rendered behind gui???
        self.travelersprite = pygame.image.load("assets/sprites/traveler_2.png").convert_alpha()

        self.gui_s2_travelerimage = pygame_gui.elements.UIImage(pygame.Rect((96+16, 8), (32, 32)), self.travelersprite, game.guimanager, container=self.gui_creatorwindow)
        
        self.gui_s2_firstnametext = pygame_gui.elements.UILabel(pygame.Rect((4, 32), (256, 22)), "First Name", game.guimanager, self.gui_creatorwindow)
        self.gui_s2_firstname = pygame_gui.elements.UITextEntryLine(pygame.Rect((0, 48), (254, 24)), game.guimanager, self.gui_creatorwindow)
        
        self.gui_s2_lastnametext = pygame_gui.elements.UILabel(pygame.Rect((4, 68), (256, 22)), "Last Name", game.guimanager, self.gui_creatorwindow)
        self.gui_s2_lastname = pygame_gui.elements.UITextEntryLine(pygame.Rect((0, 84), (254, 24)), game.guimanager, self.gui_creatorwindow)
        
        self.gui_s2_skincolortext = pygame_gui.elements.UILabel(pygame.Rect((4, 142), (256, 22)), "Skin Color", game.guimanager, self.gui_creatorwindow)
        self.gui_s2_skincolor = pygame_gui.elements.UIPanel(pygame.Rect((0, 164), (254, 96)), 0, game.guimanager, container=self.gui_creatorwindow)
        self.gui_s2_skincolor.r = pygame_gui.elements.UIHorizontalSlider(pygame.Rect((0, 0), (254, 24)), 255, (0, 255), game.guimanager, self.gui_s2_skincolor)
        self.gui_s2_skincolor.g = pygame_gui.elements.UIHorizontalSlider(pygame.Rect((0, 24), (254, 24)), 255, (0, 255), game.guimanager, self.gui_s2_skincolor)
        self.gui_s2_skincolor.b = pygame_gui.elements.UIHorizontalSlider(pygame.Rect((0, 48), (254, 24)), 255, (0, 255), game.guimanager, self.gui_s2_skincolor)
        
        self.gui_s2_randomizebutton = pygame_gui.elements.UIButton(pygame.Rect((0, 250), (254, 24)), "Randomize", game.guimanager, self.gui_creatorwindow)
        
        self.gui_s2.append(self.gui_s2_travelerimage)
        self.gui_s2.append(self.gui_s2_firstname)
        self.gui_s2.append(self.gui_s2_firstnametext)
        self.gui_s2.append(self.gui_s2_lastname)
        self.gui_s2.append(self.gui_s2_lastnametext)
        self.gui_s2.append(self.gui_s2_randomizebutton)
        self.gui_s2.append(self.gui_s2_skincolor)
        self.gui_s2.append(self.gui_s2_skincolortext)
        self.gui_s2.append(self.gui_s2_skincolor.r)
        self.gui_s2.append(self.gui_s2_skincolor.g)
        self.gui_s2.append(self.gui_s2_skincolor.b)
        
        
    def RandomizeTraveler(self):
        firstnames = []
        lastnames = []
        
        with open("assets/text/fnames.txt", "r") as firstnamesfile:
            firstnames = firstnamesfile.read().splitlines()
            firstnamesfile.close()
        
        with open("assets/text/lnames.txt", "r") as lastnamesfile:
            lastnames = lastnamesfile.read().splitlines()
            lastnamesfile.close()
        
        self.gui_s2_firstname.set_text(f"{random.choice(firstnames)}")
        self.gui_s2_lastname.set_text(f"{random.choice(lastnames)}")
        
        self.gui_s2_skincolor.r.set_current_value(random.randint(0, 255))
        self.gui_s2_skincolor.g.set_current_value(random.randint(0, 255))
        self.gui_s2_skincolor.b.set_current_value(random.randint(0, 255))
        
    def updateGUI(self):
        if self.page == 1:
            for element in self.gui_s1:
                element.show()
        else:
            for element in self.gui_s1:
                element.hide()
                
        if self.page == 2:
            for element in self.gui_s2:
                element.show()
        else:
            for element in self.gui_s2:
                element.hide()
        
        self.gui_s2_travelerimage.image = self.travelersprite.copy()
        self.gui_s2_travelerimage.image.fill((self.gui_s2_skincolor.r.get_current_value(), self.gui_s2_skincolor.g.get_current_value(), self.gui_s2_skincolor.b.get_current_value()), special_flags=pygame.BLEND_RGB_MULT)

        if self.page == 3:
            self.SaveData()
    
    def GUIButtonPressed(self, button):
        super().GUIButtonPressed(button)
        
        if button == self.gui_backbutton:
            if self.page > 1:
                self.page -= 1
        elif button == self.gui_nextbutton:
            if self.page < 3:
                self.page += 1
        elif button == self.gui_s2_randomizebutton:
            self.RandomizeTraveler()
            
    def SaveData(self):
        self.save.data["difficulty"] = self.gui_s1_difficulty.selected_option
        self.save.data["travelers"] = []
        self.save.data["travelers"].append(
            {
                "x": 1024,
                "y": 1024,
                "firstname": self.gui_s2_firstname.get_text(),
                "lastname": self.gui_s2_lastname.get_text(),
                "skincolor":{
                    "r": self.gui_s2_skincolor.r.get_current_value(),
                    "g": self.gui_s2_skincolor.g.get_current_value(),
                    "b": self.gui_s2_skincolor.b.get_current_value()
                }
            })
        self.save.save()
        game.changeFrame(GameFrame)
                
class LoadingFrame(Frame):
    newFrame = None
    
    def __init__(self, newFrame):
        super().__init__()
        self.newFrame = newFrame
    
    def frameUpdate(self):
        super().frameUpdate()
        game.guimanager.clear_and_reset()
        asyncio.run(self.LoadAssets())
        game.Frame = self.newFrame()
        
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
            game.changeFrame(CharacterCreatorFrame)
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
            self.sprite.image = pygame.image.load(newtexture).convert_alpha()
            self.texture = newtexture
        except:
            print(f"Texture {self.texture} does not exist!")
            self.texture = "assets/sprites/missing.png"
            self.sprite.image = pygame.image.load(self.texture).convert()

    def draw(self, screen):
        if self.Visible:
            if Utils.IsOnScreen(self.Position, self.Size):
                #if ent is traveler, draw sprite with skincolor tint
                sprite = self.sprite.image.copy()
                if isinstance(self, Traveler):
                    sprite.fill((self.skincolor), special_flags=pygame.BLEND_RGB_MULT)
                screen.blit(sprite, self.Position - game.Frame.Camera.Position)
        
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
    
    def Tick(self):
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
    
    firstname = "John"
    lastname = "Doe"
    skincolor = (255, 255, 255)
    
    ai_state = 1 #0 = stopped, 1 = wandering, 2 = moving to destination
    destinationPosition = pygame.Vector2(0, 0)
    
    def __init__(self):
        super().__init__()
        
    def draw(self, screen):
        super().draw(screen)
        
        if Utils.IsOnScreen(self.Position) and Utils.IsMouseHovering(self):
            nameText = pygame.font.SysFont("microsoftsansserif", 9).render(f"{self.firstname} {self.lastname}", False, "white")
            nameTextShadow = pygame.font.SysFont("microsoftsansserif", 9).render(f"{self.firstname} {self.lastname}", False, "black")
            screen.blit(nameTextShadow, (self.Position.x + self.Size.x / 2 - nameText.get_width() / 2 - game.Frame.Camera.Position.x + 1, self.Position.y - 24 - game.Frame.Camera.Position.y + 1))
            screen.blit(nameText, (self.Position.x + self.Size.x / 2 - nameText.get_width() / 2 - game.Frame.Camera.Position.x, self.Position.y - 24 - game.Frame.Camera.Position.y))
            
            healthText = pygame.font.SysFont("microsoftsansserif", 9).render(f"{self.Health} HP", False, "white")
            healthTextShadow = pygame.font.SysFont("microsoftsansserif", 9).render(f"{self.Health} HP", False, "black")
            screen.blit(healthTextShadow, (self.Position.x + self.Size.x / 2 - healthText.get_width() / 2 - game.Frame.Camera.Position.x + 1, self.Position.y - 12 - game.Frame.Camera.Position.y + 1))
            screen.blit(healthText, (self.Position.x + self.Size.x / 2 - healthText.get_width() / 2 - game.Frame.Camera.Position.x, self.Position.y - 12 - game.Frame.Camera.Position.y))
        
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
    
class Utils:
    def IsOnScreen(position, size=(32, 32)):
        if position.x + size[0] > game.Frame.Camera.Position.x and position.x < game.Frame.Camera.Position.x + SCREEN_WIDTH and position.y + size[1] > game.Frame.Camera.Position.y and position.y < game.Frame.Camera.Position.y + SCREEN_HEIGHT:
            return True
        else:
            return False
        
    def IsMouseHovering(entity):
        if pygame.mouse.get_pos()[0] + game.Frame.Camera.Position.x > entity.Position.x and pygame.mouse.get_pos()[0] + game.Frame.Camera.Position.x < entity.Position.x + entity.Size.x and pygame.mouse.get_pos()[1] + game.Frame.Camera.Position.y > entity.Position.y and pygame.mouse.get_pos()[1] + game.Frame.Camera.Position.y < entity.Position.y + entity.Size.y:
            return True
        else:
            return False
    
game = Game()
game.run()