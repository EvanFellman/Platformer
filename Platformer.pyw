from PIL import Image
from copy import deepcopy
import pygame

pygame.init()
GRAVITY = -0.1

SCREEN_WIDTH = 80  # best if its divisible by 2
SCREEN_HEIGHT = 50
player = 0
screen = pygame.display.set_mode((SCREEN_WIDTH * 10, SCREEN_HEIGHT * 10))
pygame.display.set_caption("By: Evan Fellman")
level = 0
savedCoords = []
sortedCoords = []
colors = ["blue", "green"]
gateColorsOn = {
    "blue": (40, 80, 170),
    "green": (40, 170, 80)
}
gateColorsOff = {
    "blue": (50, 50, 50),
    "green": (50, 50, 50)
    # "blue": (26, 57, 114),
    # "green": (26, 114, 57)
}
switchColorsOn = {
    "blue": (70, 130, 240),
    "green": (70, 240, 130)
}
switchColorsOff = {
    "blue": (60, 100, 210),
    "green": (60, 210, 100)
}


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
        pygame.draw.rect(screen, self.appearance, ((SCREEN_WIDTH * 5) + ((self.getx() - midx) * 10),
                                                   SCREEN_HEIGHT * 5 - ((self.gety() - midy) * 10) - 10, 10, 10))

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
midx: int = player.getx()
midy: int = player.gety()
deathBelow = []
startingPoints = []
level = 0
numLevels = 0


def reset():
    global level
    global player
    global midx
    global midy
    global sortedCoords
    global savedCoords
    global before
    global after
    level += 1
    player = Player(startingPoints[level])
    midx = player.getx()
    midy = player.gety()
    sortedCoords = [deepcopy(x) for x in savedCoords]
    for y in range(round(midy - (SCREEN_HEIGHT / 2)), round(midy + (SCREEN_HEIGHT / 2)))[::-1]:
        for x in range(midx - round(SCREEN_WIDTH / 2), midx + round(SCREEN_WIDTH / 2)):
            thing = sortedCoords[level].get(str(x) + "," + str(y))
            if player.getx() == x and player.gety() == y:
                player.show(screen)
                thingg = sortedCoords[level].get(str(x) + "," + str(y - 1))
                if thingg is not None and thingg[0] == "enemy":
                    if player.dy < GRAVITY:
                        sortedCoords[level].pop(str(x) + "," + str(y - 1))
                if thing is not None:
                    if thing[0] == "enemy":
                        level -= 1
                        reset()
                    elif thing[0] == "fin":
                        reset()
            elif thing is None:
                pygame.draw.rect(screen, (0, 0, 0), ((SCREEN_WIDTH * 5) + ((x - midx) * 10),
                                                         SCREEN_HEIGHT * 5 - ((y - midy) * 10) - 10, 10, 10))
            else:
                thing[1].show(screen)
                thing[1].move(level)
    before = {}
    after = {}


def death():
    global level
    level -= 1
    reset()


aaa: int = 0
while True:
    img = 5
    try:
        img = Image.open("level" + str(aaa) + ".jpg")
    except:
        try:
            img = Image.open("level" + str(aaa) + ".png")
        except:
            break
    img = img.convert("RGB")
    startingPoints.append([])
    numLevels += 1
    sortedCoords.append({})
    deathBelow.append(-1)
    gates = {}
    switches = {}
    for c in colors:
        gates[c] = []
        switches[c] = []
    for j in range(img.height):
        for i in range(img.width):
            r, g, b = img.getpixel((i, j))
            if r < 20 and g < 20 and b < 20:
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = ("wall", Wall(i, (-1) + img.height - j))
            elif r < 20 and g > 240 and b < 20:
                startingPoints[aaa] = (i, (-1) + img.height - j)
            elif r < 20 and g < 20 and b > 240:
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = \
                    ("fin", NextLevel(i, (-1) + img.height - j))
            elif r > 240 and g > 240 and b < 20:
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = ("enemy", Enemy(i, (-1) +
                                                                                               img.height - j, 0, 0))
            elif r > 240 and g < 20 and b < 20:
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = (
                "bad spot", BadSpot(i, (-1) + img.height - j))
            # blue switches and gates
            elif r < 20 and g < 20 and 200 < b < 240:
                a = Switch(i, (-1) + img.height - j, "blue", True, [])
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = (a.name, a)
                switches["blue"].append(a)
            elif r < 20 and g < 20 and 180 < b < 200:
                a = Gate(i, (-1) + img.height - j, "blue", True)
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = (a.name, a)
                gates["blue"].append(a)
            elif r < 20 and g < 20 and 160 < b < 180:
                a = Gate(i, (-1) + img.height - j, "blue", False)
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = (a.name, a)
                gates["blue"].append(a)
            # green switches and gates
            elif r < 20 and 200 < g < 240 and b < 20:
                a = Switch(i, (-1) + img.height - j, "green", True, [])
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = (a.name, a)
                switches["green"].append(a)
            elif r < 20 and 180 < g < 200 and b < 20:
                a = Gate(i, (-1) + img.height - j, "green", True)
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = (a.name, a)
                gates["green"].append(a)
            elif r < 20 and 160 < g < 180 and b < 20:
                a = Gate(i, (-1) + img.height - j, "green", False)
                sortedCoords[aaa][str(i) + "," + str((-1) + img.height - j)] = (a.name, a)
                gates["green"].append(a)
    for c in colors:
        for s in switches[c]:
            s.gates = gates[c]
    aaa += 1
player = Player(startingPoints[0])
level = 0
savedCoords = [deepcopy(x) for x in sortedCoords]
before = {}
after = {}
while True:
    timeElapsed = pygame.time.get_ticks()
    pressed = pygame.key.get_pressed()
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
                        level -= 1
                        reset()
                        reseted = True
                    elif thing[0] == "fin":
                        reset()
                        reseted = True
                a = sortedCoords[level].get(str(player.getx()) + "," + str(player.gety()))
                if a is not None and (player.dx != 0 or player.dy != GRAVITY):
                    if "switch" in a[0]:
                        a[1].flip(level)
            elif thing is None:
                if before.get(str(midx - x) + "," + str(midy - y)) is not None:
                    pygame.draw.rect(screen, (0, 0, 0), ((SCREEN_WIDTH * 5) + ((x - midx) * 10),
                                                 SCREEN_HEIGHT * 5 - ((y - midy) * 10) - 10, 10, 10))
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
    while player.getx() < midx - (SCREEN_WIDTH / 4):
        midx -= 1
    while player.getx() > midx + (SCREEN_WIDTH / 4):
        midx += 1
    while player.gety() < midy - (SCREEN_HEIGHT / 4):
        midy -= 1
    while player.gety() > midy + (SCREEN_HEIGHT / 4):
        midy += 1
    if player.gety() <= deathBelow[level]:
        level -= 1
        reset()
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
    if pressed[pygame.K_SPACE]:
        midx = player.getx()
        midy = player.gety()
    if pressed[pygame.K_RETURN]:
        multiplier = 5
    if pressed[pygame.K_KP8]:
        SCREEN_HEIGHT += 2 * multiplier
        screen = pygame.display.set_mode((SCREEN_WIDTH * 10, SCREEN_HEIGHT * 10))
        before = {}
    if pressed[pygame.K_KP2]:
        SCREEN_HEIGHT -= 2 * multiplier
        screen = pygame.display.set_mode((SCREEN_WIDTH * 10, SCREEN_HEIGHT * 10))
        before = {}
    if pressed[pygame.K_KP4]:
        SCREEN_WIDTH -= 4 * multiplier
        screen = pygame.display.set_mode((SCREEN_WIDTH * 10, SCREEN_HEIGHT * 10))
        before = {}
    if pressed[pygame.K_KP6]:
        SCREEN_WIDTH += 4 * multiplier
        screen = pygame.display.set_mode((SCREEN_WIDTH * 10, SCREEN_HEIGHT * 10))
        before = {}
    pygame.event.pump()
    pygame.display.flip()
    while pygame.time.get_ticks() - timeElapsed < 1000 / 30:
        pass
