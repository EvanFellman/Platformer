from PIL import Image
import pygame
from os import remove
from copy import deepcopy
level = 0
openLevel = {}
pygame.init()
myfont = pygame.font.SysFont('impact', 20)
previousLevelTxt = {}
lvlNumberTxt = {}
nextLevelTxt = {}
wallTxt = {}
startTxt = {}
goalTxt = {}
badSpotTxt = {}
enemyTxt = {}
greenSwitchTxt = {}
greenGateOnTxt = {}
greenGateOffTxt = {}
blueSwitchTxt = {}
blueGateOnTxt = {}
blueGateOffTxt = {}
eraserTxt = {}
saveTxt = {}
testTxt = {}
pixelSize = 15
txtHeight = 3 + myfont.get_linesize() - myfont.get_descent()
SCREEN_HEIGHT = round((txtHeight / pixelSize) + 0.5) + 40
SCREEN_WIDTH = 80
screen = pygame.display.set_mode((SCREEN_WIDTH * 15, SCREEN_HEIGHT * 15))
previousLevelTxt[0] = myfont.render(" < ", False, (0, 0, 0), (255, 255, 255))
screen.blit(previousLevelTxt[0], (0, 0))
previousLevelTxt[1] = 0
timerToRedrawSaveButton = -1
midx = 0
midy = 0
beforeErase = "wall"
start = (0, 0)
beforeMovedWithMouse = (-1, -1, -1, -1)
beforeLineDrawn = (None, None)
player = 0
GRAVITY = -0.1
isTesting = False
startingPoint = 0
appearances = {
    "wall": (255, 255, 255),
    "start": (0, 0, 255),
    "goal": (0, 255, 0),
    "bad spot": (255, 0, 0),
    "blue switch": (70, 130, 240),
    "green switch": (70, 240, 130),
    "blue gate off": (26, 57, 114),
    "green gate off": (26, 114, 57),
    "blue gate on": (40, 80, 170),
    "green gate on": (40, 170, 80),
    "enemy": (255, 128, 0),
    "erase": (0, 0, 0)
}
colors = ["blue", "green"]
gateColorsOn = {
    "blue": (40, 80, 170),
    "green": (40, 170, 80)
}
gateColorsOff = {
    "blue": (50, 50, 50),
    "green": (50, 50, 50)
}
switchColorsOn = {
    "blue": (70, 130, 240),
    "green": (70, 240, 130)
}
switchColorsOff = {
    "blue": (60, 100, 210),
    "green": (60, 210, 100)
}
sortedCoords = {}


class Object:
    def __init__(self, x: int = None, y: int = None, dx: int = None, dy: int = None, appearance=None):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.appearance = appearance
        self.name = "Object"

    def getx(self):
        return round(self.x)

    def gety(self):
        return round(self.y)

    def getdx(self):
        return self.dx

    def getdy(self):
        return self.dy

    def setdx(self, new_dx):
        self.dx = new_dx

    def setdy(self, new_dy):
        self.dy = new_dy

    def show(self, screen):
        pygame.draw.rect(screen, self.appearance, ((SCREEN_WIDTH * 10) + ((self.getx() - midx) * 20) - 200,
                                                   SCREEN_HEIGHT * 10 - ((self.gety() - midy) * 20) - 100, 20, 20))

    def move(self, level=None):
        pass

    def touching(self, a):
        return a.getx() == self.getx() and a.gety() == self.gety()


class Player(Object):
    def __init__(self, startingPoint=None):
        if startingPoint is None:
            Object.__init__(self, 0, 0, 0, 0, (0, 0, 255))
        else:
            Object.__init__(self, startingPoint[0], startingPoint[1], 0, 0, (0, 0, 255))
        self.name = "player"

    def move(self, level=None):
        self.setdx(0)
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
            self.setdx(1)
        elif pressed[pygame.K_a] or pressed[pygame.K_LEFT]:
            self.setdx(-1)
        if sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(self.gety())) is not None and \
                "wall" in sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(self.gety()))[0]:
            self.setdx(0)
        if (pressed[pygame.K_w] or pressed[pygame.K_UP]) and \
                sortedCoords[level].get(str(self.getx()) + "," + str(round(self.y + self.dy))) is not None and \
                "wall" in sortedCoords[level].get(str(self.getx()) + "," + str(round(self.y + self.dy)))[0]:
            self.setdy(1)
        if sortedCoords[level].get(str(self.getx()) + "," + str(round(self.y + self.dy))) is not None and \
                "wall" in sortedCoords[level].get(str(self.getx()) + "," + str(round(self.y + self.dy)))[0]:
            self.setdy(0)
            while sortedCoords[level].get(str(self.getx()) + "," + str(round(self.y + self.dy))) is not None and \
                    "wall" in sortedCoords[level].get(str(self.getx()) + "," + str(round(self.y + self.dy)))[0]:
                self.y -= GRAVITY
        if sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(round(self.y + self.dy))) is not None and \
                "wall" in sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(round(self.y + self.dy)))[0]:
            self.setdx(0)
        self.x += self.dx
        self.y += self.dy
        if self.dy > -0.5:
            self.dy += GRAVITY
        if sortedCoords[level].get(str(self.getx()) + "," + str(self.gety())) is not None and \
                isinstance(sortedCoords[level].get(str(self.getx()) + "," + str(self.gety()))[1], BadSpot):
            death()
            return
        if sortedCoords[level].get(str(self.getx()) + "," + str(self.gety() - 1)) is not None and \
                isinstance(sortedCoords[level].get(str(self.getx()) + "," + str(self.gety() - 1))[1], BadSpot):
            death()
            return
        for i in range(-1, 2)[::2]:
            if sortedCoords[level].get(str(self.getx() + i) + "," + str(self.gety())) is not None and \
                    isinstance(sortedCoords[level].get(str(self.getx() + i) + "," + str(self.gety()))[1], BadSpot):
                death()
                return


class Wall(Object):
    def __init__(self, x, y):
        Object.__init__(self, x, y, None, None, (255, 255, 255))
        self.name = "wall"

    def move(self, level=None):
        pass


class BadSpot(Object):
    def __init__(self, x, y):
        Object.__init__(self, x, y, None, None, (255, 0, 0))
        self.shouldShow = player.y >= self.y
        self.name = "bad spot"

    def show(self, screen):
        if player.y >= self.y:
            Object.show(self, screen)
        else:
            a = Object(self.x, self.y, None, None, (0, 0, 0))
            a.show(screen)


class NextLevel(Object):
    def __init__(self, x, y):
        Object.__init__(self, x, y, None, None, (0, 255, 0))
        self.name = "next level"

    def move(self, level=None):
        pass


class Switch(Object):
    def __init__(self, x: int, y: int, color: str, on: bool, gates=[]):
        self.on = on
        self.gates = gates
        self.color = color
        if self.on:
            Object.__init__(self, x, y, 0, 0, switchColorsOn[self.color])
        else:
            Object.__init__(self, x, y, 0, 0, switchColorsOff[self.color])
        self.updateName()
        self.wasDrawn = True

    def updateName(self):
        self.name = "switch " + str(self.on) + " " + self.color

    def flip(self, level):
        if not self.wasDrawn:
            return
        self.wasDrawn = False
        if self.on:
            self.appearance = switchColorsOff[self.color]
        else:
            self.appearance = switchColorsOn[self.color]
        self.on = not self.on
        for a in self.gates:
            a.flip(level)
        self.updateName()
        sortedCoords[level][str(self.getx()) + "," + str(self.gety())] = (self.name, self)

    def show(self, screen):
        self.wasDrawn = True
        Object.show(self, screen)


class Gate(Object):
    def __init__(self, x: int, y: int, color, on: bool):
        self.color = color
        self.on = on
        if self.on:
            Object.__init__(self, x, y, None, None, gateColorsOn[self.color])
        else:
            Object.__init__(self, x, y, None, None, gateColorsOff[self.color])
        self.updateName()

    def setOn(self, on: bool):
        self.on = on
        if self.on:
            self.appearance = gateColorsOn[self.color]
        else:
            self.appearance = gateColorsOff[self.color]
        self.updateName()

    def flip(self, level):
        self.setOn(not self.on)
        sortedCoords[level][str(self.getx()) + "," + str(self.gety())] = (self.name, self)

    def updateName(self):
        if self.on:
            self.name = "wall gate"
        else:
            self.name = "gate " + str(self.on) + " " + self.color


class Enemy(Object):
    def __init__(self, x, y, dx, dy):
        Object.__init__(self, x, y, dx, dy, (255, 128, 0))
        self.name = "enemy"

    def move(self, level):
        global sortedCoords
        sortedCoords[level].pop(str(self.getx()) + "," + str(self.gety()))
        if self.getx() > player.getx() + 3:
            self.dx = -0.2
        elif self.getx() < player.getx() - 3:
            self.dx = 0.2
        if self.dx == 0:
            if self.getx() < player.getx():
                self.dx = 0.2
            elif self.getx() > player.getx():
                self.dx = -0.2
        if sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(self.gety())) is not None and \
                "wall" in sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(self.gety()))[0] and \
                sortedCoords[level].get(str(self.getx()) + "," + str(self.gety() - 1)) is not None:
            self.setdy(0.65)
        if sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(self.gety())) is not None:
            self.setdx(0)
        if sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(self.gety() - 1)) is None:
            f = True
            for wowie in range(2, 7):
                if sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(self.gety() - wowie)) is not None:
                    f = False
                    break
            if f:
                f = False
                for i in range(1, 5):
                    for wowie in range(-5, 5):
                        t = 1
                        if self.dx != 0:
                            t = abs(self.dx) / self.dx
                        else:
                            break
                        if sortedCoords[level].get(str(round(self.x + self.dx + (i * t))) +
                                                   "," + str(self.gety() - wowie)) is not None:
                            f = True
                            break
                if f and sortedCoords[level].get(str(self.getx()) + "," + str(self.gety() - 1)) is not None:
                    self.setdy(1)
                elif sortedCoords[level].get(str(self.getx()) + "," + str(self.gety() - 1)) is not None:
                    self.setdx(0)
        if sortedCoords[level].get(str(self.getx()) + "," + str(round(self.y + self.dy))) is not None:
            self.setdy(0)
        if sortedCoords[level].get(str(round(self.x + self.dx)) + "," + str(round(self.y + self.dy))) is not None:
            self.setdx(0)
        self.x += self.dx
        self.y += self.dy
        if self.dy > -0.5:
            self.dy += GRAVITY
        if sortedCoords[level].get(str(self.getx()) + "," + str(self.gety() - 1)) is not None and \
                isinstance(sortedCoords[level].get(str(self.getx()) + "," + str(self.gety() - 1))[1], BadSpot):
            return
        for i in range(-1, 2)[::2]:
            if sortedCoords[level].get(str(self.getx() + i) + "," + str(self.gety())) is not None and \
                    isinstance(sortedCoords[level].get(str(self.getx() + i) + "," + str(self.gety()))[1], BadSpot):
                return
        sortedCoords[level][str(self.getx()) + "," + str(self.gety())] = ("enemy", self)


player: Player = Player()


def loadLevel(aaa: int):
    global openLevel
    openLevel = {}
    screen.fill((230, 230, 230))
    screen.blit(previousLevelTxt[0], (0, 0))     
    x = myfont.size(" < ")[0]
    lvlNumberTxt[0] = myfont.render("level " + str(aaa + 1), False, (0, 0, 0), (255, 255, 255))
    screen.blit(lvlNumberTxt[0], (x, 0))
    lvlNumberTxt[1] = x
    x += myfont.size("level " + str(level + 1))[0]
    nextLevelTxt[0] = myfont.render(" > ", False, (0, 0, 0), (255, 255, 255))
    screen.blit(nextLevelTxt[0], (x, 0))
    nextLevelTxt[1] = x
    x += myfont.size(" > ")[0]
    wallTxt[0] = myfont.render(" Wall ", False, (255, 255, 255), (50, 50, 50))
    screen.blit(wallTxt[0], (x, 0))
    wallTxt[1] = x
    x += myfont.size(" Wall ")[0]
    startTxt[0] = myfont.render(" Start ", False, (255, 255, 255), (0, 0, 255))
    screen.blit(startTxt[0], (x, 0))
    startTxt[1] = x
    x += myfont.size(" Start ")[0]
    goalTxt[0] = myfont.render(" Goal ", False, (255, 255, 255), (0, 255, 0))
    screen.blit(goalTxt[0], (x, 0))
    goalTxt[1] = x
    x += myfont.size(" Goal ")[0]
    badSpotTxt[0] = myfont.render(" :( ", False, (255, 255, 255), (255, 0, 0))
    screen.blit(badSpotTxt[0], (x, 0))
    badSpotTxt[1] = x
    x += myfont.size(" :( ")[0]
    enemyTxt[0] = myfont.render(" Enemy ", False, (255, 255, 255), (255, 128, 0))
    screen.blit(enemyTxt[0], (x, 0))
    enemyTxt[1] = x
    x += myfont.size(" Enemy ")[0]
    greenSwitchTxt[0] = myfont.render(" Switch ", False, (255, 255, 255), (70, 240, 130))
    screen.blit(greenSwitchTxt[0], (x, 0))
    greenSwitchTxt[1] = x
    x += myfont.size(" Switch ")[0]
    greenGateOnTxt[0] = myfont.render(" Closed Gate ", False, (255, 255, 255), (40, 170, 80))
    screen.blit(greenGateOnTxt[0], (x, 0))
    greenGateOnTxt[1] = x
    x += myfont.size(" Closed Gate ")[0]
    greenGateOffTxt[0] = myfont.render(" Open Gate ", False, (255, 255, 255), (26, 114, 57))
    screen.blit(greenGateOffTxt[0], (x, 0))
    greenGateOffTxt[1] = x
    x += myfont.size(" Open Gate ")[0]
    blueSwitchTxt[0] = myfont.render(" Switch ", False, (255, 255, 255), (70, 130, 240))
    screen.blit(blueSwitchTxt[0], (x, 0))
    blueSwitchTxt[1] = x
    x += myfont.size(" Switch ")[0]
    blueGateOnTxt[0] = myfont.render(" Closed Gate ", False, (255, 255, 255), (40, 80, 170))
    screen.blit(blueGateOnTxt[0], (x, 0))
    blueGateOnTxt[1] = x
    x += myfont.size(" Closed Gate ")[0]
    blueGateOffTxt[0] = myfont.render(" Open Gate ", False, (255, 255, 255), (26, 57, 114))
    screen.blit(blueGateOffTxt[0], (x, 0))
    blueGateOffTxt[1] = x
    x += myfont.size(" Open Gate ")[0]
    eraserTxt[0] = myfont.render("  Erase  ", False, (0, 0, 0), (100, 100, 100))
    screen.blit(eraserTxt[0], (x, 0))
    eraserTxt[1] = x
    x += myfont.size("  Erase  ")[0]
    saveTxt[0] = myfont.render("  SAVE  ", False, (0, 0, 0), (255, 255, 255))
    screen.blit(saveTxt[0], (x, 0))
    saveTxt[1] = x
    x += myfont.size("  SAVE  ")[0]
    testTxt[0] = myfont.render("  TEST  ", False, (0, 0, 0), (255, 0, 255))
    screen.blit(testTxt[0], (x, 0))
    testTxt[1] = x
    x += myfont.size("  TEST  ")[0]
    img = None
    try:
        img = Image.open("level" + str(aaa) + ".jpg")
    except:
        try:
            img = Image.open("level" + str(aaa) + ".png")
        except:
            return


    for j in range(img.height):
        for i in range(img.width):
            r, g, b = img.getpixel((i, j))
            if r < 20 and g < 20 and b < 20:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "wall"
            elif r < 20 and g > 240 and b < 20:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "start"
                global midx
                global midy
                global start
                midx = i
                midy = (-1) + img.height - j
                start = (midx, midy)
            elif r < 20 and g < 20 and b > 240:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "goal"
            elif r > 240 and g > 240 and b < 20:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "enemy"
            elif r > 240 and g < 20 and b < 20:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "bad spot"
            elif r < 20 and g < 20 and 200 < b < 240:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "blue switch"
            elif r < 20 and g < 20 and 180 < b < 200:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "blue gate on"
            elif r < 20 and g < 20 and 160 < b < 180:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "blue gate off"
            elif r < 20 and 200 < g < 240 and b < 20:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "green switch"
            elif r < 20 and 180 < g < 200 and b < 20:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "green gate on"
            elif r < 20 and 160 < g < 180 and b < 20:
                openLevel[str(i) + "," + str((-1) + img.height - j)] = "green gate off"


def save():
    pygame.draw.rect(screen, (255, 255, 0), (saveTxt[1], 0, myfont.size(" SAVE   ")[0], txtHeight - 5))
    minX, minY, maxX, maxY = 9E99, 9E99, -9E99, -9E99
    for key, value in openLevel.items():
        wowieDuderThatsCrazyThanksABunch = key.split(",")
        x = int(wowieDuderThatsCrazyThanksABunch[0])
        y = int(wowieDuderThatsCrazyThanksABunch[1])
        if x < minX:
            minX = x
        if x > maxX:
            maxX = x
        if y < minY:
            minY = y
        if y > maxY:
            maxY = y
    aaaaa = pygame.Surface((maxX + 1 - minX, maxY + 1 - minY))
    aaaaa.fill((255, 255, 255))
    final = pygame.PixelArray(aaaaa)
    for key, value in openLevel.items():
        wowieDuderThatsCrazyThanksABunch = key.split(",")
        x = int(wowieDuderThatsCrazyThanksABunch[0])
        y = int(wowieDuderThatsCrazyThanksABunch[1])
        x = (x - minX)
        y = (maxY - minY) - (y - minY)
        final[x, y] = appearances[value]
        if value == "wall":
            final[x, y] = (0, 0, 0)
        if value == "start":
            final[x, y] = (0, 255, 0)
        if value == "goal":
            final[x, y] = (0, 0, 255)
        if value == "enemy":
            final[x, y] = (255, 255, 0)
        apple = 0
        if "switch" in value:
            apple = 220
        if "gate on" in value:
            apple = 190
        if "gate off" in value:
            apple = 170
        if apple > 0:
            if "blue" in value:
                final[x, y] = (0, 0, apple)
            elif "green" in value:
                final[x, y] = (0, apple, 0)
    try:
        Image.open("level" + str(level) + ".jpg")
        remove("level" + str(level) + ".jpg")
    except:
        pass
    pygame.image.save(final.make_surface(), "level" + str(level) + ".png")
    global timerToRedrawSaveButton
    timerToRedrawSaveButton = 30


def test():
    global isTesting
    global sortedCoords
    global startingPoint
    global player
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, 5000, 5000))
    isTesting = True
    sortedCoords[level] = {}
    switches = {
        "green": [],
        "blue": []
    }
    gates = {
        "green": [],
        "blue": []
    }
    minX, minY, maxX, maxY = 9E99, 9E99, -9E99, -9E99
    for key, value in openLevel.items():
        wowieDuderThatsCrazyThanksABunch = key.split(",")
        x = int(wowieDuderThatsCrazyThanksABunch[0])
        y = int(wowieDuderThatsCrazyThanksABunch[1])
        if x < minX:
            minX = x
        if x > maxX:
            maxX = x
        if y < minY:
            minY = y
        if y > maxY:
            maxY = y
    for key, value in openLevel.items():
        wowieDuderThatsCrazyThanksABunch = key.split(",")
        x = int(wowieDuderThatsCrazyThanksABunch[0]) - minX
        y = int(wowieDuderThatsCrazyThanksABunch[1]) - minY
        if value == "wall":
            a = Wall(x, y)
            sortedCoords[level][str(x) + "," + str(y)] = a.name, a
        elif value == "goal":
            a = NextLevel(x, y)
            sortedCoords[level][str(x) + "," + str(y)] = a.name, a
        elif value == "bad spot":
            a = BadSpot(x, y)
            sortedCoords[level][str(x) + "," + str(y)] = a.name, a
        elif "switch" in value:
            if "blue" in value:
                a = Switch(x, y, "blue", True, [])
                switches["blue"].append(a)
                sortedCoords[level][str(x) + "," + str(y)] = a.name, a
            else:
                a = Switch(x, y, "green", True, [])
                switches["green"].append(a)
                sortedCoords[level][str(x) + "," + str(y)] = a.name, a
        elif "gate" in value:
            if "blue" in value:
                a = Gate(x, y, "blue", "on" in value)
                gates["blue"].append(a)
                sortedCoords[level][str(x) + "," + str(y)] = a.name, a
            else:
                a = Gate(x, y, "green", "on" in value)
                gates["green"].append(a)
                sortedCoords[level][str(x) + "," + str(y)] = a.name, a
        elif "enemy" == value:
            a = Enemy(x, y, 0, 0)
            sortedCoords[level][str(x) + "," + str(y)] = a.name, a
        elif "start" == value:
            startingPoint = (x, y)
            player = Player(startingPoint)
    for i in switches["green"]:
        i.gates = gates["green"]
    for i in switches["blue"]:
        i.gates = gates["blue"]
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, 5000, 5000))


def death():
    global isTesting
    global level
    global before
    global after
    isTesting = False
    loadLevel(level)
    before = {}
    after = {}


def draw():
    pygame.draw.rect(screen, (0, 0, 0), (0, txtHeight - 2, pixelSize * SCREEN_WIDTH, (pixelSize * SCREEN_HEIGHT) - txtHeight))
    w, h = SCREEN_WIDTH, round(((SCREEN_HEIGHT * pixelSize) - txtHeight) / pixelSize)
    for y in range(round(midy - ((h / 2) * 15 / pixelSize)), round(midy + ((h / 2) * 15 / pixelSize)))[::-1]:
        for x in range(midx - round(15 * w / (2 * pixelSize)), midx + round(15 * w / (2 * pixelSize))):
            a = openLevel.get(str(x) + "," + str(y))
            if a is None:
                continue
            else:
                pygame.draw.rect(screen, appearances[a], (pixelSize * (w / 2 + x - midx),  -pixelSize * (y - midy) + (0.7 * pixelSize) * txtHeight, pixelSize, pixelSize))


loadLevel(0)
mouseMode = "wall"
sinceLastLevelAdjustment = pygame.time.get_ticks()
before = {}
zflag = True
after = {}
while True:
    if not isTesting:  # edit level
        xtemp, ytemp = pygame.mouse.get_pos()
        actualX = round((xtemp / pixelSize) - ((SCREEN_WIDTH / 2) - midx) - 0.5)
        actualY = round((((ytemp - ((pixelSize * 0.7) * txtHeight)) / (-pixelSize)) + midy) + 0.5)
        if timerToRedrawSaveButton > 0:
            timerToRedrawSaveButton -= 1
            pygame.draw.rect(screen, (0, 255, 0), (saveTxt[1], 0, myfont.size(" SAVE   ")[0], txtHeight - 5))
        elif timerToRedrawSaveButton == 0:
            screen.blit(saveTxt[0], (saveTxt[1], 0))
            timerToRedrawSaveButton = -1
        startTime = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pressed = pygame.key.get_pressed()
        m = pygame.mouse.get_pressed()[0]
        if not (m and pressed[pygame.K_z]):
            zflag = True
        if not (pressed[pygame.K_SPACE] and m):
            beforeMovedWithMouse = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], midx, midy
        if m and pygame.mouse.get_pos()[1] <= txtHeight:  # if the mouse button is pressed
            x = pygame.mouse.get_pos()[0]
            if x < lvlNumberTxt[1] and level > 0 and pygame.time.get_ticks() - sinceLastLevelAdjustment >= 500:  # previous level
                sinceLastLevelAdjustment = pygame.time.get_ticks()
                if pressed[pygame.K_LSHIFT]:
                    level -= 5
                else:
                    level -= 1
                if level < 0:
                    level = 0
                loadLevel(level)
            elif nextLevelTxt[1] <= x < wallTxt[1] and pygame.time.get_ticks() - sinceLastLevelAdjustment >= 500:  # next level
                sinceLastLevelAdjustment = pygame.time.get_ticks()
                if pressed[pygame.K_LSHIFT]:
                    level += 5
                else:
                    level += 1
                loadLevel(level)
            elif x < startTxt[1]:  # wall
                beforeErase = "wall"
                mouseMode = "wall"
            elif x < goalTxt[1]:  # start
                beforeErase = "start"
                mouseMode = "start"
            elif x < badSpotTxt[1]:  # goal
                beforeErase = "goal"
                mouseMode = "goal"
            elif x < enemyTxt[1]:  # bad spot
                beforeErase = "bad spot"
                mouseMode = "bad spot"
            elif x < greenSwitchTxt[1]:  # enemy
                beforeErase = "enemy"
                mouseMode = "enemy"
            elif x < greenGateOnTxt[1]:  # green switch
                beforeErase = "green switch"
                mouseMode = "green switch"
            elif x < greenGateOffTxt[1]:  # green gate on
                beforeErase = "green gate on"
                mouseMode = "green gate on"
            elif x < blueSwitchTxt[1]:  # green gate off
                beforeErase = "green gate off"
                mouseMode = "green gate off"
            elif x < blueGateOnTxt[1]:  # blue switch
                beforeErase = "blue switch"
                mouseMode = "blue switch"
            elif x < blueGateOffTxt[1]:  # blue gate on
                beforeErase = "blue gate on"
                mouseMode = "blue gate on"
            elif x < eraserTxt[1]:  # blue gate off
                beforeErase = "blue gate off"
                mouseMode = "blue gate off"
            elif x < saveTxt[1]:  # eraser
                mouseMode = "erase"
                beforeErase = "erase"
            elif x < testTxt[1]:  # save
                save()
            else:  # test the level
                test()
                continue
        elif m:  # place a thing
            if pressed[pygame.K_SPACE]:
                midx = beforeMovedWithMouse[2] - round((pygame.mouse.get_pos()[0] - beforeMovedWithMouse[0]) / 10)
                midy = beforeMovedWithMouse[3] + round((pygame.mouse.get_pos()[1] - beforeMovedWithMouse[1]) / 10)
                draw()
            elif pressed[pygame.K_z] and not mouseMode == "erase" and zflag:
                zflag = False
                sinceLastLevelAdjustment = pygame.time.get_ticks()
                print(beforeLineDrawn)
                if beforeLineDrawn[0] is None or (beforeLineDrawn[0] == actualX and beforeLineDrawn[1] == actualY):
                    beforeLineDrawn = (actualX, actualY)
                else:
                    x, y = pygame.mouse.get_pos()
                    actualX = round((x / pixelSize) - ((SCREEN_WIDTH / 2) - midx) - 0.5)
                    actualY = round((((y - ((pixelSize * 0.7) * txtHeight)) / (-pixelSize)) + midy) + 0.5)
                    dx = actualX - beforeLineDrawn[0]
                    dy = actualY - beforeLineDrawn[1]
                    i = beforeLineDrawn[0]
                    j = beforeLineDrawn[1]
                    a = 0
                    while a < 10000:
                        openLevel[str(round(i)) + "," + str(round(j))] = mouseMode
                        i += dx / 10000
                        j += dy / 10000
                        a += 1
                    beforeLineDrawn = (None, None)
                    draw()
            elif pressed[pygame.K_LALT]:
                if openLevel.get(str(actualX) + "," + str(actualY)) is not None:
                    mouseMode = openLevel[str(actualX) + "," + str(actualY)]
                    beforeErase = mouseMode
            else:
                w, h = pixelSize * SCREEN_WIDTH, pixelSize * SCREEN_HEIGHT - txtHeight
                x, y = pygame.mouse.get_pos()
                actualX = round((x / pixelSize) - ((SCREEN_WIDTH / 2) - midx) - 0.5)
                actualY = round((((y - ((pixelSize * 0.7) * txtHeight)) / (-pixelSize)) + midy) + 0.5)
                openLevel[str(actualX) + "," + str(actualY)] = mouseMode
                if mouseMode == "erase":
                    openLevel.pop(str(actualX) + "," + str(actualY))
                    if pressed[pygame.K_LSHIFT]:
                        for i in range(-1, 2):
                            for j in range(-1, 2):
                                try:
                                    openLevel.pop(str(actualX + i) + "," + str(actualY + j))
                                except:
                                    pass
        if pressed[pygame.K_UP]:
            if pressed[pygame.K_LSHIFT] and pygame.time.get_ticks() - sinceLastLevelAdjustment >= 300:
                midy += SCREEN_HEIGHT
                sinceLastLevelAdjustment = pygame.time.get_ticks()
            else:
                midy += 1
        if pressed[pygame.K_DOWN]:
            if pressed[pygame.K_LSHIFT] and pygame.time.get_ticks() - sinceLastLevelAdjustment >= 300:
                midy -= SCREEN_HEIGHT
                sinceLastLevelAdjustment = pygame.time.get_ticks()
            else:
                midy -= 1
        if pressed[pygame.K_LEFT]:
            if pressed[pygame.K_LSHIFT] and pygame.time.get_ticks() - sinceLastLevelAdjustment >= 300:
                midx -= SCREEN_WIDTH
                sinceLastLevelAdjustment = pygame.time.get_ticks()
            else:
                midx -= 1
        if pressed[pygame.K_RIGHT]:
            if pressed[pygame.K_LSHIFT] and pygame.time.get_ticks() - sinceLastLevelAdjustment >= 300:
                midx += SCREEN_WIDTH
                sinceLastLevelAdjustment = pygame.time.get_ticks()
            else:
                midx += 1
        if pressed[pygame.K_LCTRL] and beforeErase != "erase":
            if mouseMode != "erase":
                beforeErase = mouseMode
            mouseMode = "erase"
        else:
            if beforeErase != "erase":
                mouseMode = beforeErase
        pygame.event.pump()
        pygame.display.flip()
        draw()
        while pygame.time.get_ticks() - startTime <= 1000/30:
            pass
    else:  # testing the loaded level
        timeElapsed = pygame.time.get_ticks()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_ESCAPE]:
            death()
            continue
        reseted = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        for y in range(round(midy - (SCREEN_HEIGHT / 2)), round(midy + (SCREEN_HEIGHT / 2)))[::-1]:
            for x in range(midx - round(SCREEN_WIDTH / 2), midx + round(SCREEN_WIDTH / 2)):
                thing = sortedCoords[level].get(str(x) + "," + str(y))
                if player.getx() == x and player.gety() == y:
                    player.show(screen)
                    after[str(midx - x) + "," + str(midy - y)] = player
                    thingg = sortedCoords[level].get(str(x) + "," + str(y - 1))
                    if thingg is not None and thingg[0] == "enemy":
                        if player.dy < GRAVITY:
                            sortedCoords[level].pop(str(x) + "," + str(y - 1))
                    if thing is not None:
                        if thing[0] == "enemy":
                            death()
                            reseted = True
                        elif thing[0] == "next level":
                            death()
                            reseted = True
                    a = sortedCoords[level].get(str(player.getx()) + "," + str(player.gety()))
                    if a is not None and (player.dx != 0 or player.dy != GRAVITY):
                        if "switch" in a[0]:
                            a[1].flip(level)
                elif thing is None:
                    if before.get(str(midx - x) + "," + str(midy - y)) is not None:
                        pygame.draw.rect(screen, (0, 0, 0), ((SCREEN_WIDTH * 10) + ((x - midx) * 20) - 200,
                                                             SCREEN_HEIGHT * 10 - ((y - midy) * 20) - 100, 20, 20))
                elif before.get(str(midx - x) + "," + str(midy - y)) != thing[1].name:
                    after[str(midx - x) + "," + str(midy - y)] = thing[1].name
                    thing[1].show(screen)
                    thing[1].move(level)
                else:
                    after[str(midx - x) + "," + str(midy - y)] = thing[1].name
                    thing[1].move(level)
        if reseted:
            before = {}
            after = {}
            continue
        before = deepcopy(after)
        after = {}
        if sortedCoords[level].get(str(player.getx()) + "," + str(player.gety())) is not None and \
                sortedCoords[level].get(str(player.getx()) + "," + str(player.gety()))[0] == "enemy":
            death()
            continue
        player.move(level)
        if sortedCoords[level].get(str(player.getx()) + "," + str(player.gety())) is not None and \
                sortedCoords[level].get(str(player.getx()) + "," + str(player.gety()))[0] == "enemy":
            death()
            continue
        while player.getx() < midx - (SCREEN_WIDTH / 8):
            midx -= 1
        while player.getx() > midx + (SCREEN_WIDTH / 8):
            midx += 1
        while player.gety() < midy - (SCREEN_HEIGHT / 8):
            midy -= 1
        while player.gety() > midy + (SCREEN_HEIGHT / 8):
            midy += 1
        if player.gety() < 0:
            death()
            continue
        if pressed[pygame.K_LSHIFT]:
            if player.getx() > midx + 1:
                midx += 1
            elif player.getx() < midx - 1:
                midx -= 1
            if player.gety() > midy + 1:
                midy += 1
            elif player.gety() < midy - 1:
                midy -= 1
        multiplier = 1
        pygame.event.pump()
        pygame.display.flip()
        while pygame.time.get_ticks() - timeElapsed < 1000 / 30:
            pass
