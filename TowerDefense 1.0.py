#0.9 done!!!! deleting comments here. Not including this line no.
#had debugged by Emma Zhong, jzhong1
#Resources from
#http://www.freevectors.me/100-cute-free-vector-monsters-character-illustration.html
#also from google image
#also from mini heroes
#also some code from course note, such as read/write file
#also need to thank Jack Wang, a 2107er for pygame study.


import pygame, random, sys
from pygame.locals import *
from sys import exit
import time
import math

#initial part
pygame.init()
screen = pygame.display.set_mode((640,480))

pygame.display.set_caption("Jack's Tower Defense 1.0 (Build 0042)")
black = (  0,  0,    0)
white = (255, 255, 255)
blue  = (  0,   0, 255)
green = (  0, 250, 154)
red   = (255,   0,   0)
grey  = (128, 128, 128)
clock = pygame.time.Clock()

class MonsterA(pygame.sprite.Sprite):
    def __init__(self, x=0, y=240, speed=1.3):  #not sure if default values useful or not
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("MonsterA.png").convert_alpha()
        self.power = 50  #power lower than 0 then not alive.
        self.fullPower = 50  #for drawing blood mark
        self.earn = 20  #money earned after killed
        self.speed = speed
        self.kill = 1  #if fail to kill it, cost 1.
        self.x, self.y = x,y  #position
        

class MonsterB(pygame.sprite.Sprite):
    def __init__(self, x=0, y=240, speed=1.6):  #not sure if default values useful or not
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("MonsterB.png").convert_alpha()
        self.power = 80  #power lower than 0 then not alive.
        self.fullPower = 80
        self.earn = 40  #money earned after killed
        self.speed = speed
        self.kill = 2  #if fail to kill it, cost 1.
        self.x, self.y = x,y


class AttackerA(pygame.sprite.Sprite):
    """AttackerA emits bullets"""
    def __init__(self,grade=1,x=0,y=0):  #x, y as row, col
        pygame.sprite.Sprite.__init__(self)
        #
        self.grade = grade
        #
        if self.grade == 1:
            self.image = pygame.image.load("AttackerA1.png").convert_alpha()
        elif self.grade == 2:
            self.image = pygame.image.load("AttackerA2.png").convert_alpha()
        #
        self.delay = 1.5 / self.grade #s
        self.attack = 3 * self.grade  #slowest and weaket
        self.radius = 100 * self.grade  #radius
        # higher grade: less delay, stronger and further
        #
        self.x, self.y = x, y
        self.cost = 50  #money needed to buy
        self.upgradeCost = 200
        self.attacking = None  #when meets a monster in range, is index
                               #of monsters
        self.startTime = 0
        self.endTime = 400

#
class AttackerB(pygame.sprite.Sprite):  #for slow down
    def __init__(self, grade=1, x=0, y=0):
        pygame.sprite.Sprite.__init__(self)
        self.grade = grade
        if self.grade == 1:
            self.image = pygame.image.load("AttackerB1.png").convert_alpha()
        elif self.grade == 2:
            self.image = pygame.image.load("AttackerB2.png").convert_alpha()
        #
        self.radius = 100 * self.grade
        self.slowrate = 0.7 ** self.grade
        self.x, self.y = x, y
        self.cost = 200
        self.upgradeCost = 300


class ABullet(pygame.sprite.Sprite):
    def __init__(self, bx=0, by=0, attacking=None, speed=2.2):
        pygame.sprite.Sprite.__init__(self)  #bulletxy, monsterxy
        self.image = pygame.image.load("AttackerABullet.png").convert_alpha()
        self.bx = bx
        self.by = by
        self.chasing = attacking
        self.met = False  #this might not be useful
        self.speed = speed
        self.hurt = 5


class TowerDefense(object):
    def __init__(self):
        #
        self.page = "welcome"  #"chooseLevel", "game", "levelEdit", "helpPage"
        #
        self.margin = 80  #just for upper and lower.
        self.cellsize = 32
        #
        self.chooseLevel = None  #for restart
        self.nextLevel = None
        self.passed = False
        #
        #this is to prevent levelEditInit to init the num of MAnum, MBnum
        
        self.welcomeInit()

    def levelEditInit(self):
        try:
            with open("selfMap.txt","rt") as fin:
                self.edittedMap = eval(fin.read())
        except:  #set up new file first
            self.edittedMap = [[0] * 20 for i in xrange(10)]
        if self.MAnum == None and self.MBnum == None:
            self.MAnum = 3
            self.MBnum = 3
        self.editMonster = "A"

            
    def getDirection(self, route, row, col):
        #
        direction = {}
        rightmost = len(route[0]) - 1
        blockNum = 0  #record the order of the block
        while col != rightmost:
            for (dx, dy) in [(1, 0), (0, 1), (0, -1), (-1, 0)]:
                if 0 <= row + dy < 10 and 0 <= col + dx < 20 and route[row + dy][col + dx] == 1:
                    if (dx, dy) == (1, 0) and (row, col+1) not in direction:  #there should be other paths later
                        blockNum += 1
                        direction[(row, col)] = [blockNum, "right"]
                        row += dy
                        col += dx
                        break
                    elif (dx, dy) == (0, 1) and (row+1, col) not in direction:
                        blockNum += 1
                        direction[(row, col)] = [blockNum, "down"]
                        row += dy
                        col += dx
                        break
                    elif (dx, dy) == (0, -1) and (row-1, col) not in direction:
                        blockNum += 1
                        direction[(row, col)] = [blockNum, "up"]
                        row += dy
                        col += dx
                        break
                    elif (dx, dy) == (-1, 0) and (row, col-1) not in direction:
                        blockNum += 1
                        direction[(row, col)] = [blockNum, "left"]
                        row += dy
                        col += dx
                        break
        return direction
    
        

    def getMap(self,filename="map1.txt", mode="rt"):   #direct cite from course note readFile
        with open(filename, mode) as fin:
            resultString = fin.read()
            return eval(resultString)  #now it's 2d list

    def drawTile(self,route):
        tileimage = pygame.image.load("tile.jpg").convert()
        for row in xrange(len(route)):
            for col in xrange(len(route[0])):
                if route[row][col] == 1:  #then it's route
                    screen.blit(tileimage, (col * self.cellsize, self.margin + row * self.cellsize))

    def getTowerPlace(self, route):
        for col in xrange(len(route[0])):
            for row in xrange(len(route)):
                reverseCol = len(route[0]) - 1
                if route[row][reverseCol] == 1:  #last place of route, place Tower
                    return (row, reverseCol)

    def drawTower(self, row, col):
        towerimage = pygame.image.load("tower.png").convert_alpha()  #later need to replace with transparent
        screen.blit(towerimage, (col * self.cellsize - 18, self.margin + row * self.cellsize - 58))

    def getMonsterStartPlace(self, route):  #get from left up
        for col in xrange(len(route[0])):
            for row in xrange(len(route)):
                if route[row][col] == 1:
                    return row, col

    def placeAttacker(self, mouseX, mouseY, page):
        if page == "mouseIsAttackerA":
            cost = AttackerA().cost
            AttackerList = self.AttackerAList
        elif page == "mouseIsAttackerB":
            cost = AttackerB().cost
            AttackerList = self.AttackerBList
        #first check if on the route
        col = mouseX / self.cellsize #20 cols
        row = (mouseY - self.margin) / self.cellsize
        if (0 <= row < 10 and 0 <= col < 20):
            if self.route[row][col] != 1:  #then not on route
                if self.BALANCE >= cost:  #not on route and affordable
                    add = True
                    for elem in self.AttackerAList:
                       if (elem.x, elem.y) == (col, row):  #not sure if needs () or not
                           add = False
                           break
                    for elem in self.AttackerBList:
                        if (elem.x, elem.y) == (col, row):
                            add = False
                            break
                    if add == True:
                        if page == "mouseIsAttackerA":
                            AttackerList += [AttackerA(1, col, row)]
                            self.BALANCE -= cost
                        elif page == "mouseIsAttackerB":
                            AttackerList += [AttackerB(1, col, row)]
                            self.BALANCE -= cost

    def drawBalance(self):
        font = pygame.font.Font("freesansbold.ttf",20)
        text = font.render("Balance: %d" %(self.BALANCE), 1, red)
        screen.blit(text, (5, 5))

    def drawTowerLife(self):
        font = pygame.font.Font("freesansbold.ttf",20)
        text = font.render("Tower Life: %d" %(self.towerLife), 1, red)
        screen.blit(text, (470, 5))


    def AttackerBAttack(self, elem):
        delta = 0
        for attacker in self.AttackerBList:
            aX = attacker.x * self.cellsize
            aY = attacker.y * self.cellsize + self.margin
            if (aX - elem.x) ** 2 + (aY - elem.y) ** 2 <= attacker.radius ** 2:  #here is slowdown
                if attacker.grade == 1:
                    if delta < 1:
                        delta = 1
                elif attacker.grade == 2:
                    delta = 2
                    break
        return delta


    #got route direction from map
    def MonsterMove(self, direction, monsterList):
        """10 rows, 20 cols. MonsterA move according to shape of route"""
        for i in xrange(len(monsterList)):
            #first get place
            elem = monsterList[i]
            if elem.x < 0:  #if not yet in the screen
                elem.x = elem.x + elem.speed
            else:
                # determining for attackerB : slow down
                if self.AttackerBAttack(elem) == 0:
                    speed = elem.speed
                elif self.AttackerBAttack(elem) == 1:
                    speed = elem.speed * AttackerB(1).slowrate
                elif self.AttackerBAttack(elem) == 2:
                    speed = elem.speed * AttackerB(2).slowrate
                #
                mrow = int((elem.y - self.margin) / self.cellsize)  
                mcol = int(elem.x / self.cellsize)
                if (mrow, mcol) in direction:
                    if direction[(mrow, mcol)][1] == "right":  
                        if (mrow+1, mcol) in direction and direction[(mrow+1, mcol)][1] == "up":
                            if elem.y - speed > mrow * self.cellsize + self.margin:
                                elem.y = elem.y - speed  #make the offset
                            else:
                                elem.x = elem.x + speed
                        else:
                            elem.x = elem.x + speed
                    elif direction[(mrow, mcol)][1] == "left":
                        if (mrow+1, mcol) in direction and direction[(mrow+1, mcol)][1] == "up":
                            if elem.y - speed > mrow * self.cellsize + self.margin:
                                elem.y = elem.y - speed  #make the offset
                            else:
                                elem.x = elem.x - speed
                        else:
                            elem.x = elem.x - speed
                    elif direction[(mrow, mcol)][1] == "down":
                        if (mrow, mcol+1) in direction and direction[(mrow, mcol+1)][1] == "left":
                            if elem.x - speed > mcol * self.cellsize:
                                elem.x = elem.x - speed  #make the offset
                            else:
                                elem.y = elem.y + speed
                        else:
                            elem.y = elem.y + speed
                    elif direction[(mrow, mcol)][1] == "up":
                        if (mrow, mcol+1) in direction and direction[(mrow, mcol+1)][1] == "left":
                            if elem.x - speed > mcol * self.cellsize:
                                elem.x = elem.x - speed
                            else:
                                elem.y = elem.y - speed
                        else:
                            elem.y = elem.y - speed


    def AttackerAttack(self, attackers):  #so not workable
        for j in xrange(len(attackers)):  #fix one of the attackerA
            elem = attackers[j]
            a = elem.x * self.cellsize
            b = self.margin + self.cellsize * elem.y  #change back to the "x", "y"
            hasTarget = False
            #
            attackingA = None
            reverseI = None
            for i in xrange(len(self.MonsterAList)):
                reverseI = len(self.MonsterAList) - i - 1
                monster = self.MonsterAList[reverseI]
                if (((a - monster.x) ** 2 + (b - monster.y) ** 2) ** 0.5 <= elem.radius and
                    monster.power > 0):  #died then must not emit bullet
                    hasTarget = True
                    attackingA = reverseI  #A means attacking Monster A, index is the index of MonsterA
                                    #it's attacking  #maybe not reverse, could change later
            #
            attackingB = None
            reverseJ = None
            for j in xrange(len(self.MonsterBList)):  
                reverseJ = len(self.MonsterBList) - j - 1
                monster = self.MonsterBList[reverseJ]
                if (((a - monster.x) ** 2 + (b - monster.y) ** 2) ** 0.5 <= elem.radius and
                    monster.power > 0):  #died then must not emit bullet
                    hasTarget = True
                    attackingB = reverseJ  #B means...
            #then compare which one is more important
            #which is to compare elem.attackingB and A
            #first get both monsters place, then compare their blockNum

            #get blockNum
            #A:
            if reverseI == None:
                attackingA = None
            else:
                aCol = int(self.MonsterAList[reverseI].x / self.cellsize)
                aRow = int((self.MonsterAList[reverseI].y - self.margin) / self.cellsize)
                if aCol < 0:
                    attackingA = None
                else:
                    determineA = self.direction[(aRow, aCol)][0] #the num
            #B:
            if reverseJ == None:
                attackingB = None
            else:
                bCol = int(self.MonsterBList[reverseJ].x / self.cellsize)
                bRow = int((self.MonsterBList[reverseJ].y - self.margin) / self.cellsize)
                if bCol < 0:
                    attackingB = None
                else:
                    determineB = self.direction[(bRow, bCol)][0] #the num
            
            #
            if attackingA == None and attackingB == None:
                hasTarget = False
            elif attackingA == None:
                elem.attacking = "B%d" %(attackingB)
            elif attackingB == None:
                elem.attacking = "A%d" %(attackingA)
            else:  #both are not none
                if determineB >= determineA:
                    elem.attacking = "B%d" %(attackingB)
                else:
                    elem.attacking = "A%d" %(attackingA)
            #
            if hasTarget == False:
                elem.attacking = None
            if attackers == self.AttackerAList:  #elif attackers == blah blah
                a += self.cellsize / 2  #optimizing place of bullet
                b += self.cellsize / 2
                self.AEmitBullet(elem, a, b)  #elem here is a class of attackerA

    def AEmitBullet(self, elem, a, b):
        #determine if time is fired first
        elem.endTime = time.time()
        if elem.endTime - elem.startTime >= elem.delay:
            elem.endTime = time.time()
            elem.startTime = time.time()  #reset
            if elem.attacking != None:
                #later determine which Monster
                if self.newSpeed != None:  #if inside survival mode...
                    self.BulletList += [ABullet(a, b, elem.attacking, self.newSpeed)]
                elif self.newSpeed == None:
                    self.BulletList += [ABullet(a, b, elem.attacking)]
        else:
            pass
        
    def BulletUpdate(self):  #1. update place
        #2. if met, disappear. 3. if out of screen, then disappear as well
        for bullet in self.BulletList:
            if bullet.bx < 0 or bullet.bx > 640 or bullet.by < 0 or bullet.by > 480:
                self.BulletList.remove(bullet)
                continue  #k. that part works.
            
            index = int(bullet.chasing[1:])
            #in case that the monster had died
            try:
                #this is added part
                if bullet.chasing[0] == "A":
                    target = self.MonsterAList[index]
                elif bullet.chasing[0] == "B":
                    target = self.MonsterBList[index]
                #Now I got the target
                    
                targetX, targetY = target.x + self.cellsize / 2, target.y + self.cellsize / 2  #op the place
                if (targetX - bullet.bx) == 0:
                    if targetY >= bullet.by:
                        angleRad = math.pi / 2
                    elif targetY < bullet.by:
                        angleRad = - math.pi / 2
                else:
                    angleRad = math.atan(float(targetY - bullet.by) / (targetX - bullet.bx))
                    if targetX > bullet.bx:
                        bullet.bx += bullet.speed * math.cos(angleRad)
                        bullet.by += bullet.speed * math.sin(angleRad)
                    elif targetX < bullet.bx:
                        bullet.bx -= bullet.speed * math.cos(angleRad)
                        bullet.by -= bullet.speed * math.sin(angleRad)
                #
                if (targetX - bullet.bx) ** 2 + (targetY - bullet.by) ** 2 <= 50:
                    self.BulletList.remove(bullet)
                    target.power -= bullet.hurt
                
            except:
                self.BulletList.remove(bullet)  #no monster then do nothing
            
                    
    def rotateAttackerA(self, x, y, z, grade):
        if z == None:
            angle = 0
        else:
            #
            target = int(z[1:])
            if z[0] == "A":
                mlist = self.MonsterAList
            elif z[0] == "B":
                mlist = self.MonsterBList
            #
            if target < len(mlist):
                monster = mlist[target]  #now I have coord of monster target
                xCo = x * self.cellsize
                yCo = y * self.cellsize + self.margin
                if xCo != monster.x:
                    slope = float(yCo - monster.y) / (xCo - monster.x)
                    angle = math.degrees(math.atan(slope))
                    if monster.y >= yCo and monster.x > xCo:
                        angle = - abs(angle) + 180
                    elif monster.y >= yCo and monster.x < xCo:
                        angle = abs(angle) 
                    elif monster.y < yCo and monster.x > xCo:
                        angle = abs(angle) + 180
                    elif monster.y < yCo and monster.x < xCo:
                        angle = - abs(angle)
                        
                else:
                    if monster.y >= yCo:  #monster below
                        angle = 90
                    elif monster.y < yCo:
                        angle = -90
            
        rotatedImage = pygame.transform.rotate(AttackerA(grade).image, angle)#debugged by Emma Zhong, jzhong1
        return rotatedImage

    def removeMonsterAndBullet(self, elem, monsters):
        if type(elem) == MonsterA:
            index = self.MonsterAList.index(elem)
            for bullet in self.BulletList:
                if bullet.chasing == "A%s"%(index):
                    self.BulletList.remove(bullet)
        elif type(elem) == MonsterB:
            index = self.MonsterBList.index(elem)
            for bullet in self.BulletList:
                if bullet.chasing == "B%s"%(index):
                    self.BulletList.remove(bullet)
        monsters.remove(elem)

    def monsterUpdate(self, monsters):
        for elem in monsters:
            if elem.power <= 0:
                self.removeMonsterAndBullet(elem, monsters)
                #also remove the bullet following it
                self.BALANCE += elem.earn
                

        for elem in monsters:
            col, row = int(elem.x / self.cellsize), int((elem.y - self.margin) / self.cellsize)
            if row == self.towerRow and col == self.towerCol:
                self.removeMonsterAndBullet(elem, monsters)
                self.towerLife -= elem.kill


    def drawWelcome(self):
        image = pygame.image.load("welcomePage.jpg").convert()
        screen.blit(image, (0, 0))
        if self.welcomeMouseAt == "Play!":
            font = pygame.font.Font("freesansbold.ttf",40)
            text = font.render("Play!", 1, green)
            screen.blit(text, (28, 375))
        else:
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("Play!", 1, green)
            screen.blit(text, (35, 380))
        #
        if self.welcomeMouseAt == "Level Edit!":
            font = pygame.font.Font("freesansbold.ttf",40)
            text = font.render("Level Edit!", 1, green)
            screen.blit(text, (180, 375))
        else:
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("Level Edit!", 1, green)
            screen.blit(text, (190, 380))
        #
        if self.welcomeMouseAt == "Help!":
            font = pygame.font.Font("freesansbold.ttf",40)
            text = font.render("Help!", 1, green)
            screen.blit(text, (453, 375))
        else:
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("Help!", 1, green)
            screen.blit(text, (460, 380))
        #
        if self.welcomeMouseAt == "High score!":
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("High Score!", 1, white)
            screen.blit(text, (320, 75))
        else:
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("High Score!", 1, white)
            screen.blit(text, (330, 80))
        #
        if self.welcomeMouseAt == "Continue!":
            font = pygame.font.Font("freesansbold.ttf",40)
            text = font.render("Continue!", 1, green)
            screen.blit(text, (21, 295))
        else:
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("Continue!", 1, green)
            screen.blit(text, (30, 300))
        #
        if self.noContinue == "showing":
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("No Record...", 1, red)
            screen.blit(text, (270, 300))
        ###
        
    def chooseLevelInit(self):
        pass  #moved to welcome init
        
    def welcomeControl(self, mouseX, mouseY, event):
        #for recording
        self.nextLevel = None
        self.welcomeMouseAt = None
        #
        self.levelEditInit()  #it has the MAnum, MBnum
        #
        self.resumeTime = time.time()  #for "continue" timer.
        #
        if 35 <= mouseX <= 108 and 380 <= mouseY <= 410:
            self.welcomeMouseAt = "Play!"
            if event.type == MOUSEBUTTONDOWN:
                self.page = "chooseLevel"
                self.chooseLevelInit()
        elif 190 <= mouseX <= 345 and 380 <= mouseY <= 405:
            self.welcomeMouseAt = "Level Edit!"
            if event.type == MOUSEBUTTONDOWN:
                #inits for levelEdit part
                self.page = "levelEdit"
        elif 450 <= mouseX <= 540 and 375 <= mouseY <= 405:
            self.welcomeMouseAt = "Help!"
            if event.type == MOUSEBUTTONDOWN:
                self.page = "helpPage"
        elif 30 <= mouseX <= 175 and 295 <= mouseY <= 325:
            self.welcomeMouseAt = "Continue!"
            if event.type == MOUSEBUTTONDOWN:
                try:
                    self.continueGame()
                except:
                    self.noContinue = True
        elif 330 <= mouseX <= 445 and 80 <= mouseY <= 95:
            self.welcomeMouseAt = "High score!"
            if event.type == MOUSEBUTTONDOWN:
                self.page = "highScore"
        #
        if self.noContinue == True:
            self.showNoContinueStart = time.time()
            self.noContinue = "showing"
        now = time.time()
        if now - self.showNoContinueStart >= 5:
            self.noContinue = False
            

    def drawchooseLevel(self, mouseX, mouseY):
        image = pygame.image.load("chooseLevel.jpg").convert()
        scaled = pygame.transform.scale(image, (640, 480))
        screen.blit(scaled, (0, 0))
        #
        font = pygame.font.Font("freesansbold.ttf",30)
        text = font.render("Level 1", 1, green)
        screen.blit(text, (160, 140))
        #
        font = pygame.font.Font("freesansbold.ttf",30)
        text = font.render("Level 2", 1, green)
        screen.blit(text, (160, 270))
        #
        font = pygame.font.Font("freesansbold.ttf",30)
        text = font.render("Level 3", 1, green)
        screen.blit(text, (160, 400))
        #
        font = pygame.font.Font("freesansbold.ttf",30)
        text = font.render("Level 4", 1, green)
        screen.blit(text, (435, 140))
        #
        font = pygame.font.Font("freesansbold.ttf",30)
        text = font.render("Survival", 1, green)
        screen.blit(text, (435, 270))
        #
        font = pygame.font.Font("freesansbold.ttf",30)
        text = font.render("Editted Level", 1, green)
        screen.blit(text, (400, 400))
        #
        font = pygame.font.Font("freesansbold.ttf", 25)
        text = font.render("<<Back", 1, green)
        screen.blit(text, (40, 30))
        #
        font = pygame.font.Font("freesansbold.ttf",30)
        text = font.render("Choose Your Level!", 1, green)
        screen.blit(text, (270, 30))
        #
        if 30 <= mouseX <= 130 and 20 <= mouseY <= 60 or self.nextLevel == 5:
            pygame.draw.rect(screen, green, Rect(30, 20, 100, 40), 5)
        elif 30 <= mouseX <= 305 and 90 <= mouseY <= 190 or self.nextLevel == 1:
            pygame.draw.rect(screen, green, Rect(30, 90, 275, 100),5)
        elif 30 <= mouseX <= 305 and 220 <= mouseY <= 320 or self.nextLevel == 2:
            pygame.draw.rect(screen, green, Rect(30, 220, 275, 100), 5)
        elif 30 <= mouseX <= 305 and 350 <= mouseY <= 450 or self.nextLevel == 3:
            pygame.draw.rect(screen, green, Rect(30, 350, 275, 100), 5)
        elif 335 <= mouseX <= 610 and 90 <= mouseY <= 190 or self.nextLevel == 4:
            pygame.draw.rect(screen, green, Rect(335, 90, 275, 100), 5)
        elif 335 <= mouseX <= 610 and 220 <= mouseY <= 320:
            pygame.draw.rect(screen, green, Rect(335, 220, 275, 100), 5)
        elif 335 <= mouseX <= 610 and 350 <= mouseY <= 450:
            pygame.draw.rect(screen, green, Rect(335, 350, 275, 100), 5)
        
        #
        if self.passed == True:
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("passed!", 1, red)
            screen.blit(text, (140, 50))
        if self.noEdit == "showing":
            font = pygame.font.Font("freesansbold.ttf",17)
            text = font.render("Self-Edit not yet implemented", 1, red)
            screen.blit(text, (200, 70))

    def chooseLevelUpdate(self):
        if self.noEdit == True:
            self.showIllegalStart = time.time()
            self.noEdit = "showing"
        self.showEnd = time.time()
        if self.showEnd - self.showIllegalStart >= 5:
            self.noEdit = False
        

    def chooseLevelControl(self, mouseX=0, mouseY=0):
        #the self.chooseLevel is for recording current state to use later.
        #1,2,3,4,"survival", "edit".
        if 30 <= mouseX <= 130 and 20 <= mouseY <= 60 or self.nextLevel == "welcome":  #another way to call #5 then back to welcome
            self.page = "welcome"
            if self.nextLevel == 5:
                self.passed = True
        elif 30 <= mouseX <= 305 and 90 <= mouseY <= 190 or self.nextLevel == 1:
            self.monsterTowerInit("map1.txt", "A6", "B5")
            self.page = "game"
            self.chooseLevel = ["map1.txt", "A6", "B5", 1]
        elif 30 <= mouseX <= 305 and 220 <= mouseY <= 320 or self.nextLevel == 2:
            self.monsterTowerInit("map2.txt", "A8", "B10")
            self.page = "game"
            self.chooseLevel = ["map2.txt", "A8", "B10", 2]
        elif 30 <= mouseX <= 305 and 350 <= mouseY <= 450 or self.nextLevel == 3:
            self.monsterTowerInit("map3.txt", "A15", "B15")
            self.page = "game"
            self.chooseLevel = ["map3.txt", "A15", "B15", 3]
        elif 335 <= mouseX <= 610 and 90 <= mouseY <= 190 or self.nextLevel == 4:
            self.monsterTowerInit("map4.txt", "A25", "B23")
            self.page = "game"
            self.chooseLevel = ["map4.txt", "A25", "B23", 4]
        elif 335 <= mouseX <= 610 and 220 <= mouseY <= 320:
            self.monsterTowerInitSurvival("map5.txt")
            self.page = "game"
            self.survivalMode = True
            self.chooseLevel = ["map5.txt", "A30", "B27", "survival"]  
        elif 335 <= mouseX <= 610 and 350 <= mouseY <= 450:
            try:
                self.monsterTowerInit("selfMap.txt", "A%d"%(self.MAnum), "B%d"%(self.MBnum))
                self.page = "game"
                self.chooseLevel = ["selfMap.txt", "A%d"%(self.MAnum), "B%d"%(self.MBnum), "edit"]
            except:
                self.noEdit = True

        self.gameStartTime = time.time() #this time would be taken, until gone to other pages,
                                        #such as game, or back to welcome.

    def monsterTowerInit(self, mapfile = None, monsterA = None, monsterB = None):
        #
        self.newSpeed = None  #for updating the speed of bullet in survival mode
        #
        self.recordTime = None  #for recording time
        #
        self.nextLevel = None
        self.gamePause = True
        self.survivalMode = False
        #For win/lose Update
        self.win = None
        self.towerLife = 10 #life of the tower
        self.BALANCE = 500
        self.AttackerAList = []
        self.AttackerBList = []
        #
        self.BulletList = []
        #
        self.route = self.getMap(mapfile) #now I have 2d list of route
        self.towerRow, self.towerCol = self.getTowerPlace(self.route)  #now I have the place for tower
        row, col = self.getMonsterStartPlace(self.route)
        #
        self.direction = self.getDirection(self.route, row, col)  #row,col is for start place,
                                                                #direction as dictionary.
        x = col * self.cellsize
        y = row * self.cellsize + self.margin
        if monsterA == None:
            self.MonsterAList = []
        elif monsterA != None:
            self.MonsterAList = []
            if monsterA[0] == "A":
                num = int(monsterA[1:])
                for i in xrange(num):
                    self.MonsterAList += [MonsterA(-70 * i + x, y)]

        #
        if monsterB == None:
            self.MonsterBList = []
        elif monsterB != None:
            self.MonsterBList = []
            if monsterB[0] == "B":
                start = len(self.MonsterAList) * (-70)
                num = int(monsterB[1:])
                for i in xrange(num):
                    self.MonsterBList += [MonsterB(-70 * i + start, y)]

    def monsterTowerInitSurvival(self, mapfile):
        self.newSpeed = None #this is for updating speed of bullet, only in survival mode
        self.nextLevel = None
        self.gamePause = True
        #For win/lose Update
        self.win = None
        self.towerLife = 10 #life of the tower
        self.BALANCE = 500
        self.AttackerAList = []
        self.AttackerBList = []
        self.MonsterAList = []
        self.MonsterBList = []
        #
        self.BulletList = []
        #
        self.route = self.getMap(mapfile) #now I have 2d list of route
        self.towerRow, self.towerCol = self.getTowerPlace(self.route)  #now I have the place for tower
        row, col = self.getMonsterStartPlace(self.route)
        self.direction = self.getDirection(self.route, row, col)  #row,col is for start place,
                                                                  #direction as dictionary.
        x = col * self.cellsize
        y = row * self.cellsize + self.margin
        self.startX, self.startY = x, y
        #
        self.MonsterAList = [MonsterA(x, y), MonsterA(x - 30, y),MonsterA(x - 60, y),MonsterA(x - 90, y),MonsterA(x - 120, y),
                            MonsterA(x - 160, y),MonsterA(x - 180, y),MonsterA(x - 220, y),MonsterA(x - 300, y)]

    def survivalModeUpdate(self):
        while self.win == None and len(self.MonsterAList) + len(self.MonsterBList) <= 5:
            if len(self.MonsterAList) >= len(self.MonsterBList):
                chooseList = self.MonsterAList
            else:
                chooseList = self.MonsterBList
            chooseObjectSpeed = chooseList[-1].speed
            newSpeed = chooseObjectSpeed + 0.1
            choice = random.randint(1,2)
            #
            if choice == 1:
                self.MonsterAList += [MonsterA(self.startX, self.startY, newSpeed)]
            elif choice == 2:
                self.MonsterBList += [MonsterB(self.startX, self.startY, newSpeed)]
            self.newSpeed = newSpeed + 1  #anyway faster than monster

    def drawlevelEdit(self, mouseX, mouseY):
        if self.page in ["levelEdit", "LEblock", "LEclear"]:
            image = pygame.image.load("LEbg.jpg").convert()
            scaled = pygame.transform.scale(image, (640, 480))
            screen.blit(scaled, (0, 0))
            #
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("Make your own map!", 1, red)
            screen.blit(text, (200,30))
            #
            pygame.draw.rect(screen, green, Rect(30, 20, 160, 40), 3)
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("<<Back & Save", 1, red)
            screen.blit(text, (35, 30))
            #
            font = pygame.font.Font("freesansbold.ttf",16)
            text = font.render("Press Left to clear All", 1, green)
            screen.blit(text, (400,400))
        #
        #
        for i in xrange(len(self.edittedMap)):
            for j in xrange(len(self.edittedMap[0])):
                if self.edittedMap[i][j] == 0:
                    pygame.draw.rect(screen, green, Rect((j*self.cellsize, self.margin+i*self.cellsize), (self.cellsize, self.cellsize)),1)
                elif self.edittedMap[i][j] == 1:
                    pygame.draw.rect(screen, green, Rect((j*self.cellsize, self.margin+i*self.cellsize), (self.cellsize, self.cellsize)))
        ###
        if self.page == "levelEdit":
            pygame.draw.rect(screen, green, Rect(40, 420, 80, 40), 3)
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("Block", 1, red)
            screen.blit(text, (50, 430))
            #
            pygame.draw.rect(screen, green, Rect(430, 20, 160, 40), 3)
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("Back no Save", 1, red)
            screen.blit(text, (440, 30))
            #
            font = pygame.font.Font("freesansbold.ttf", 16)
            text = font.render("MA%d, MB%d"%(self.MAnum, self.MBnum), 1, red) 
            screen.blit(text, (410, 440))
            #
            if self.editMonster == "A":
                showText = "Changing MonsterA num"
            elif self.editMonster == "B":
                showText = "Changing MonsterB num"
            font = pygame.font.Font("freesansbold.ttf", 16)
            text = font.render(showText, 1, red) 
            screen.blit(text, (410, 460))
            
        ###
        elif self.page == "LEblock":
            pygame.draw.rect(screen, green, Rect(40, 420, 80, 40), 3)
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("Mouse", 1, red)
            screen.blit(text, (50, 430))
            #
            cursor = pygame.image.load("LEblock.png").convert_alpha()
            scaled = pygame.transform.scale(cursor, (32, 32))
            screen.blit(scaled, (mouseX - 23, mouseY - 23))
            pygame.draw.rect(screen, green, Rect(200, 420, 80, 40), 3)
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("delete", 1, red)
            screen.blit(text, (200, 420))
            #
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("block", 1, red)
            screen.blit(text, (200, 440))
        ###
        elif self.page == "LEclear":
            pygame.draw.rect(screen, green, Rect(200, 420, 80, 40), 3)
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("Back to", 1, red)
            screen.blit(text, (200, 420))
            #
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("Edit", 1, red)
            screen.blit(text, (200, 440))
        ###
        elif self.page == "editIllegal":
            screen.fill(green)
            font = pygame.font.Font("freesansbold.ttf",20)
            text = font.render("Edit not Legal, Esc back", 1, red)
            screen.blit(text, (200, 420))

    def editIsLegal(self,edittedMap):
        #1 they don't stick together
        #K. forget about 1 Jack.
        #2 start place at 1st col, end 19th col
        #3 they are connected to each other

        #2       #used other helper functions that were written for other purposes
        try:
            towerRow, towerCol = self.getTowerPlace(edittedMap)
            if towerCol != 19:
                return False
            row, col = self.getMonsterStartPlace(edittedMap)
            if col != 0:
                return False
            
            #1 (actually 3)       #same
            #uses the row, col, towerRow, towerCol above
            direction = {}
            rightmost = 19  #20 cols. hard coded
            delta = 0
            while col != rightmost:
                delta += 1
                if delta >= 2:
                    return False
                for (dx, dy) in [(1, 0), (0, 1), (0, -1), (-1, 0)]:
                    if 0 <= row + dy < 10 and 0 <= col + dx < 20 and edittedMap[row + dy][col + dx] == 1:
                        if (dx, dy) == (1, 0) and (row, col+1) not in direction:  #there should be other paths later
                            direction[(row, col)] = "right"
                            row += dy
                            col += dx
                            delta -= 1
                            break
                        elif (dx, dy) == (0, 1) and (row+1, col) not in direction:
                            direction[(row, col)] = "down"
                            row += dy
                            col += dx
                            delta -= 1
                            break
                        elif (dx, dy) == (0, -1) and (row-1, col) not in direction:
                            direction[(row, col)] = "up"
                            row += dy
                            col += dx
                            delta -= 1
                            break
                        elif (dx, dy) == (-1, 0) and (row, col-1) not in direction:
                            direction[(row, col)] = "left"
                            row += dy
                            col += dx
                            delta -= 1
                            break
            return True
        except:   #what if the map totally couldn't get row, col
            return False
           

    def levelEditKeyControl(self, direction):
        if direction == "left":
            self.edittedMap = [[0] * 20 for i in xrange(10)]
        elif direction == "escape":
            self.page = "levelEdit"
        elif direction == "right":
            if self.editMonster == "A":
                self.editMonster = "B"
            elif self.editMonster == "B":
                self.editMonster = "A"
        elif direction == "up":
            if self.editMonster == "A":
                self.MAnum += 1
            elif self.editMonster == "B":
                self.MBnum += 1
        elif direction == "down":
            if self.editMonster == "A":
                if self.MAnum != 0:
                    self.MAnum -= 1
            elif self.editMonster == "B":
                if self.MBnum != 0:
                    self.MBnum -= 1

    def levelEditMouseControl(self, mouseX, mouseY):  #should change style
        row = (mouseY - self.margin) / self.cellsize
        col = mouseX / self.cellsize
        #back to welcome
        if self.page in ["levelEdit", "LEblock", "LEclear"]:  #save back
            if 30 <= mouseX <= 190 and 20 <= mouseY <= 60:
                if self.editIsLegal(self.edittedMap):
                    self.page = "welcome"
                    #save
                    contents = str(self.edittedMap)
                    with open("selfMap.txt", "wt") as fout:
                        fout.write(contents)
                elif self.editIsLegal(self.edittedMap) == False:
                    self.page = "editIllegal"
            elif 425 <= mouseX <= 590 and 15 <= mouseY <= 60:  #back without save
                self.page = "welcome"
        ###
        if self.page == "levelEdit":
            if 0 <= mouseX <= 120 and 400 <= mouseY <= 460:
                self.page = "LEblock"
        ###
        elif self.page == "LEblock":
            if 0 <= mouseX <= 120 and 400 <= mouseY <= 460:
                self.page = "levelEdit"
            elif 0 <= row < 10 and 0 <= col < 20:
                self.edittedMap[row][col] = 1
                
            elif 200 <= mouseX <= 280 and 420 <= mouseY <= 460:
                self.page = "LEclear"
        ###
        elif self.page == "LEclear":
            if 0 <= row < 10 and 0 <= col < 20:
                self.edittedMap[row][col] = 0
            elif 200 <= mouseX <= 280 and 420 <= mouseY <= 460:
                self.page = "LEblock"

    def winLoseUpdate(self):
        if len(self.MonsterAList) == 0 and len(self.MonsterBList) == 0 and self.towerLife > 0:
            self.win = True
            self.page = "game"
        elif self.towerLife <= 0:
            self.win = False
            self.page = "game"
            
    def drawHelpPage(self):
        screen.fill(white)
        page = pygame.image.load("helpPage.jpg").convert()
        screen.blit(page, (0, 0))

    def drawbloodMark(self, monsterList):
        image = pygame.image.load("bloodMarkRed.png").convert_alpha()
        for elem in monsterList:
            portion = float(elem.power) / elem.fullPower
            if portion >= 0.4:
                image = pygame.image.load("bloodMarkGreen.png").convert_alpha()
            elif portion < 0.4:
                image = pygame.image.load("bloodMarkRed.png").convert_alpha()
            w = int(25 * portion) if int(25 * portion) >= 0 else 0 
            h = 4  #25, 5 are hardcoded
            scaled = pygame.transform.scale(image, (w, h))
            screen.blit(scaled, (elem.x + 3, elem.y - 5))
            
            
    def drawGamePage(self, mouseX, mouseY):
        grassbg = pygame.image.load("grassbg.jpg").convert()
        scaled = pygame.transform.scale(grassbg, (642, 482))
        screen.blit(scaled, (0, 0))
        #
        self.drawTile(self.route)  #draw the route
        self.drawTower(self.towerRow, self.towerCol)
        self.drawBalance()
        self.drawTowerLife()
        #Another thing in here
        font = pygame.font.Font("freesansbold.ttf",15)
        text = font.render("Esc:back.  P:Play/Pause.  R:Restart", 1, red)
        screen.blit(text, (160, 5))

        #indicate the current state
        font = pygame.font.Font("freesansbold.ttf",25)
        cs = str(self.chooseLevel[3])
        text = font.render("Level: %s"%(cs), 1, red)
        screen.blit(text, (5, 50))

        #The place where I could click to --> self.mouseIsAttackerA
        screen.blit(AttackerA().image, (20, 430))
        
        #Attacker B
        screen.blit(AttackerB().image, (150, 430))
        
        #draw AttackerA
        for elem in self.AttackerAList:
            rotatedImage = self.rotateAttackerA(elem.x, elem.y, elem.attacking, elem.grade)
            screen.blit(rotatedImage, (elem.x * self.cellsize , elem.y *self.cellsize + self.margin))

        #draw AttackerB
        for elem in self.AttackerBList:
            #rotatedImage = self.rotateAttackerA(elem.x, elem.y, elem.attacking, elem.grade)
            screen.blit(elem.image, (elem.x * self.cellsize , elem.y *self.cellsize + self.margin))
                    
        #draw MonsterA
        for elem in self.MonsterAList:
            screen.blit(MonsterA().image, (elem.x,elem.y))
        self.drawbloodMark(self.MonsterAList)

        #draw MonsterB
        for elem in self.MonsterBList:
            screen.blit(MonsterB().image, (elem.x, elem.y))
        self.drawbloodMark(self.MonsterBList)

        #draw bullet
        for elem in self.BulletList:
            screen.blit(elem.image, (elem.bx, elem.by))

        #draw delete
        pygame.draw.rect(screen, red, Rect(480, 420, 40, 30))
        font = pygame.font.Font("freesansbold.ttf", 25)
        text = font.render("Del", 1, black)
        screen.blit(text, (480, 420))
        
        #draw upgrade
        pygame.draw.rect(screen, green, Rect(420, 420, 40, 30))
        font = pygame.font.Font("freesansbold.ttf", 13)
        text = font.render("Up", 1, black)
        screen.blit(text, (425, 420))
        font = pygame.font.Font("freesansbold.ttf", 13)
        text = font.render("grade", 1, black)
        screen.blit(text, (419, 433))
        #
        showTime = time.time() - self.gameStartTime
        font = pygame.font.Font("freesansbold.ttf", 13)
        text = font.render("Tik Tok: %.1f"%(showTime), 1, green)
        screen.blit(text, (500, 40))
        #

        if self.page == "mouseIsAttackerA":
            screen.blit(AttackerA().image, (mouseX - 23, mouseY - 23))
            #
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Delay:%rs"%(AttackerA().delay), 1, green)
            screen.blit(text, (55, 430))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Attack:%r"%(AttackerA().attack), 1, green)
            screen.blit(text, (55, 440))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Radius:%r"%(AttackerA().radius), 1, green)
            screen.blit(text, (55, 450))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Cost:%r"%(AttackerA().cost), 1, green)
            screen.blit(text, (55, 460))
            #
        elif self.page == "mouseIsAttackerB":
            screen.blit(AttackerB().image, (mouseX - 15, mouseY - 15))
            #
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("SlowRate:%0.2f"%(AttackerB().slowrate), 1, green)
            screen.blit(text, (180, 430))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Radius:%r"%(AttackerB().radius), 1, green)
            screen.blit(text, (180, 440))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Cost:%r"%(AttackerB().cost), 1, green)
            screen.blit(text, (180, 450))
            #
        elif self.page == "upgrading":
            font = pygame.font.Font("freesansbold.ttf", 15)
            text = font.render("Upgrading, click tower to upgrade", 1, white)
            screen.blit(text, (150, 60))
        #
        elif self.page == "delete":
            font = pygame.font.Font("freesansbold.ttf", 15)
            text = font.render("Removing, click tower to remove", 1, white)
            screen.blit(text, (150, 60))
        elif self.page == "game":
            font = pygame.font.Font("freesansbold.ttf", 15)
            text = font.render("Click a tower to build", 1, white)
            screen.blit(text, (150, 60))
            
        #win/lose
        if self.win == True:
            screen.fill(green)
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("You Won, press n to next level", 1, red)
            screen.blit(text, (100, 230))
            #
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("Esc Back", 1, red)
            screen.blit(text, (230, 270))
            #
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("Your Time:%.1fs"%(self.recordTime), 1, red)
            screen.blit(text, (180, 310))
            
            
        elif self.win == False:
            screen.fill(red)
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("You Lost", 1, black)
            screen.blit(text, (240, 210))
            #
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("Esc Back", 1, black)
            screen.blit(text, (240, 250))
            #
            font = pygame.font.Font("freesansbold.ttf",30)
            text = font.render("Press R Restart", 1, black)
            screen.blit(text, (210, 290))


    def removeAttacker(self, mouseX, mouseY):
        mrow = int((mouseY - self.margin) / self.cellsize)
        mcol = int((mouseX / self.cellsize))
        if 0 <= mrow < 10 and 0 <= mcol < 20:
            for elem in self.AttackerAList:  #there will be another attacker list
                if elem.x == mcol and elem.y == mrow:
                    self.AttackerAList.remove(elem)
            for elem in self.AttackerBList:  #there will be another attacker list
                if elem.x == mcol and elem.y == mrow:
                    self.AttackerBList.remove(elem)

    def upgrade(self, mouseX, mouseY):
        mrow = int((mouseY - self.margin) / self.cellsize)
        mcol = int(mouseX / self.cellsize)
        for elem in self.AttackerAList:
            if elem.x == mcol and elem.y == mrow:
                #this is the attacker!
                if self.BALANCE >= elem.upgradeCost:  #enough money
                    if elem.grade == 1:
                        self.AttackerAList.remove(elem)
                        self.AttackerAList += [AttackerA(2, mcol, mrow)]
                        self.BALANCE -= elem.upgradeCost
        #Then B list
        for elem in self.AttackerBList:
            if elem.x == mcol and elem.y == mrow:
                #this is the attacker!
                if self.BALANCE >= elem.upgradeCost:  #enough money
                    if elem.grade == 1:
                        self.AttackerBList.remove(elem)
                        self.AttackerBList += [AttackerB(2, mcol, mrow)]
                        self.BALANCE -= elem.upgradeCost


    def restart(self):
        if self.chooseLevel == None:
            pass
        else:
            self.gameStartTime = time.time()
            a = self.chooseLevel[0]
            b = self.chooseLevel[1]
            c = self.chooseLevel[2]
            self.monsterTowerInit(a, b, c)
            self.gamePause = True
            
    def showSpec(self, mouseX, mouseY):
        mRow = int((mouseY - self.margin) / self.cellsize)
        mCol = int(mouseX / self.cellsize)
        toShowA = None
        toShowB = None
        for elem in self.AttackerAList:
            if elem.x == mCol and elem.y == mRow:
                toShowA = elem
                break
        for elem in self.AttackerBList:
            if elem.x == mCol and elem.y == mRow:
                toShowB = elem
                break
        
        #
        if toShowA != None:  #then it's A
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Delay:%rs"%(AttackerA(elem.grade).delay), 1, green)
            screen.blit(text, (55, 430))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Attack:%r"%(AttackerA(elem.grade).attack), 1, green)
            screen.blit(text, (55, 440))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Radius:%r"%(AttackerA(elem.grade).radius), 1, green)
            screen.blit(text, (55, 450))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Cost:%r"%(AttackerA(elem.grade).cost), 1, green)
            screen.blit(text, (55, 460))
            cX = int((mCol + 0.5) * self.cellsize)
            cY = int((mRow + 0.5) * self.cellsize + self.margin)
            pygame.draw.circle(screen, green, (cX, cY), elem.radius, 1)
        elif toShowB != None:  #then it's B
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("SlowRate:%.2f"%(AttackerB(elem.grade).slowrate), 1, green)
            screen.blit(text, (180, 430))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Radius:%r"%(AttackerB(elem.grade).radius), 1, green)
            screen.blit(text, (180, 440))
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Cost:%r"%(AttackerB(elem.grade).cost), 1, green)
            screen.blit(text, (180, 450))
            cX = int((mCol + 0.5) * self.cellsize)
            cY = int((mRow + 0.5) * self.cellsize + self.margin)
            pygame.draw.circle(screen, green, (cX, cY), elem.radius, 1)
        elif toShowA == None and toShowB == None:
            #
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Click Me", 1, white)
            screen.blit(text, (55, 440))
            #
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Click Me", 1, white)
            screen.blit(text, (180, 440))

    def showRange(self, mouseX, mouseY, page):
        if page == "mouseIsAttackerA":
            elem = AttackerA()
        elif page == "mouseIsAttackerB":
            elem = AttackerB()
        #
        pygame.draw.circle(screen, green, (mouseX, mouseY), elem.radius, 1)

    def nextStage(self):
        currentLevel = self.chooseLevel[3]
        if currentLevel < 4:
            self.nextLevel = currentLevel + 1
        elif currentLevel == 4:
            self.nextLevel = "welcome"
        elif currentLevel == "edit":
            self.nextLevel = "welcome"
        self.chooseLevelControl()

    def showUpgradeCost(self, mouseX, mouseY):
        mRow = int((mouseY - self.margin) / self.cellsize)
        mCol = int(mouseX / self.cellsize)
        toShowA = None
        toShowB = None
        for elem in self.AttackerAList:
            if elem.x == mCol and elem.y == mRow:
                if elem.grade == 1:
                    toShowA = elem
                    break
        for elem in self.AttackerBList:
            if elem.x == mCol and elem.y == mRow:
                if elem.grade == 1:
                    toShowB = elem
                    break
        #
        if toShowA != None:  #then it's A
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Cost:%r"%(AttackerA(elem.grade).upgradeCost), 1, green)
            screen.blit(text, (55, 430))
            cX = int((mCol + 0.5) * self.cellsize)
            cY = int((mRow + 0.5) * self.cellsize + self.margin)
            r = AttackerA(2).radius
            pygame.draw.circle(screen, green, (cX, cY), r, 1)
        elif toShowB != None:  #then it's B
            font = pygame.font.Font("freesansbold.ttf", 13)
            text = font.render("Cost:%r"%(AttackerB(elem.grade).upgradeCost), 1, green)
            screen.blit(text, (180, 430))
            cX = int((mCol + 0.5) * self.cellsize)
            cY = int((mRow + 0.5) * self.cellsize + self.margin)
            r2 = AttackerB(2).radius
            pygame.draw.circle(screen, green, (cX, cY), r2, 1)

    def continueGame(self):
        with open("record.txt", "rt") as fin:
                record = eval(fin.read())
        #
        level = record["chooseLevel"][3]
        mapfile = "map%d.txt"%(level)
        self.monsterTowerInit(mapfile)
        #
        self.chooseLevel = record["chooseLevel"]
        self.route = record["route"]
        self.BALANCE = int(record["balance"])
        self.towerLife = int(record["towerLife"])
        self.direction = record["direction"]
        self.gameStartTime = time.time() - record["timeUsed"]   #this is how it continued
        #
        MonsterARecord = record["monsterA"]
        for elem in MonsterARecord:
            newElem = MonsterA(elem[2], elem[3], elem[1])
            newElem.power = elem[0]
            self.MonsterAList += [newElem]
        #
        MonsterBRecord = record["monsterB"]
        for elem in MonsterBRecord:
            newElem = MonsterB(elem[2], elem[3], elem[1])
            newElem.power = elem[0]
            self.MonsterBList += [newElem]
        #
        AttackerARecord = record["attackerA"]
        for elem in AttackerARecord:
            newElem = AttackerA(elem[0], elem[1], elem[2])
            self.AttackerAList += [newElem]
        #
        AttackerBRecord = record["attackerB"]
        for elem in AttackerBRecord:
            newElem = AttackerB(elem[0], elem[1], elem[2])
            self.AttackerBList += [newElem]
        #
        BulletList = record["bullets"]
        for elem in BulletList:
            newElem = ABullet(elem[0], elem[1], elem[2], elem[3])
            self.BulletList += [newElem]
        #
        self.page = "game"
        
        
    def saveGame(self):
        if (self.page in  ["game", "mouseIsAttackerA", "mouseIsAttackerB", "delete", "upgrading"] and
            self.win == None and type(self.chooseLevel[3]) == int):
            #then worth recording
            record = dict()
            #
            MonsterARecord = []
            for elem in self.MonsterAList:
                MonsterARecord += [[elem.power, elem.speed, elem.x, elem.y]]
            record["monsterA"] = MonsterARecord
            #
            MonsterBRecord = []
            for elem in self.MonsterBList:
                MonsterBRecord += [[elem.power, elem.speed, elem.x, elem.y]]
            record["monsterB"] = MonsterBRecord
            #
            AttackerARecord = []
            for elem in self.AttackerAList:
                AttackerARecord += [[elem.grade, elem.x, elem.y]]
            record["attackerA"] = AttackerARecord
            #
            AttackerBRecord = []
            for elem in self.AttackerBList:
                AttackerBRecord += [[elem.grade, elem.x, elem.y]]
            record["attackerB"] = AttackerBRecord
            #
            BulletList = []
            for elem in self.BulletList:
                BulletList += [[elem.bx, elem.by, elem.chasing, elem.speed]]
            record["bullets"] = BulletList
            #
            record["route"] = self.route
            record["direction"] = self.direction
            record["balance"] = self.BALANCE
            record["towerLife"] = self.towerLife
            record["chooseLevel"] = self.chooseLevel
            record["timeUsed"] = time.time() - self.gameStartTime
            #
            with open("record.txt", "wt") as fout:
                fout.write(str(record))

    def welcomeInit(self):
        self.noContinue = None
        self.showNoContinueStart = time.time()
        #this is for level edit. Preventing..... 
        self.MAnum = None
        self.MBnum = None
        self.noEdit = None
        self.showIllegalStart = time.time()
        #also chooseLevelEdit
        #also highScoreInit
        try:
            with open("highScore.txt", "rt") as fout:
                self.scores = eval(fout.read())
        except:
            self.scores = dict()
            with open("highScore.txt", "wt") as fin:
                fin.write(str(self.scores))

    def changeHighScore(self):
        level = self.chooseLevel[3]
        time = self.recordTime
        if level not in self.scores:
            self.scores[level] = time
        elif level in self.scores:
            delta = self.scores[level]
            if delta >= time:
                self.scores[level] = time
            else:
                pass
        #
        with open("highScore.txt", "wt") as fin:
                fin.write(str(self.scores))
        
    def drawHighScore(self):
        image = pygame.image.load("highScorePage.jpg").convert_alpha()
        screen.blit(image, (0, 0))
        #
        font = pygame.font.Font("freesansbold.ttf", 25)
        text = font.render("High Score", 1, black)
        screen.blit(text, (270, 40))
        #
        font = pygame.font.Font("freesansbold.ttf", 25)
        text = font.render("Level 1", 1, green)
        screen.blit(text, (60, 250))
        font = pygame.font.Font("freesansbold.ttf", 25)
        text = font.render("Level 2", 1, green)
        screen.blit(text, (60, 290))
        font = pygame.font.Font("freesansbold.ttf", 25)
        text = font.render("Level 3", 1, green)
        screen.blit(text, (60, 330))
        font = pygame.font.Font("freesansbold.ttf", 25)
        text = font.render("Level 4", 1, green)
        screen.blit(text, (60, 370))
        font = pygame.font.Font("freesansbold.ttf", 25)
        text = font.render("Level Edit", 1, green)
        screen.blit(text, (60, 410))
        ###
        if 1 in self.scores:
            t = self.scores[1]
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("%.2fs"%(t), 1, green)
            screen.blit(text, (340, 250))
        else:
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("None", 1, grey)
            screen.blit(text, (340, 250))
        #
        if 2 in self.scores:
            t = self.scores[2]
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("%.2fs"%(t), 1, green)
            screen.blit(text, (340, 290))
        else:
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("None", 1, grey)
            screen.blit(text, (340, 290))
        #
        if 3 in self.scores:
            t = self.scores[3]
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("%.2fs"%(t), 1, green)
            screen.blit(text, (340, 330))
        else:
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("None", 1, grey)
            screen.blit(text, (340, 330))
        #
        if 4 in self.scores:
            t = self.scores[4]
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("%.2fs"%(t), 1, green)
            screen.blit(text, (340, 370))
        else:
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("None", 1, grey)
            screen.blit(text, (340, 370))
        #
        if "edit" in self.scores:
            t = self.scores["edit"]
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("%.2fs"%(t), 1, green)
            screen.blit(text, (340, 410))
        else:
            font = pygame.font.Font("freesansbold.ttf", 25)
            text = font.render("None", 1, grey)
            screen.blit(text, (340, 410))
        ###
        font = pygame.font.Font("freesansbold.ttf", 18)
        text = font.render("Esc Back.", 1, black)
        screen.blit(text, (220, 430)) 
    
    def run(self):
        while True:
            #
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.saveGame()
                    pygame.quit()
                    sys.exit()
                mouseX, mouseY = pygame.mouse.get_pos()
                if event.type == MOUSEBUTTONDOWN:
                    if self.page in ["game", "mouseIsAttackerA", "delete", "upgrading","mouseIsAttackerB"]:
                        #
                        if 26 <= mouseX <= 141 and 430 <= mouseY <= 465:
                            if self.page == "mouseIsAttackerA":
                                self.page = "game"
                            elif self.page in ["game", "delete", "mouseIsAttackerB", "upgrading"]:
                                self.page = "mouseIsAttackerA"
                        elif 420 <= mouseX <= 455 and 420 <= mouseY <= 445:
                            if self.page == "upgrading":
                                self.page = "game"
                            elif self.page in ["game", "delete", "mouseIsAttackerA", "mouseIsAttackerB"]:
                                self.page = "upgrading"
                        elif 150 <= mouseX <= 265 and 430 <= mouseY <= 465:
                            if self.page == "mouseIsAttackerB":
                                self.page = "game"
                            elif self.page in ["game", "delete", "mouseIsAttackerA", "upgrading"]:
                                self.page = "mouseIsAttackerB"
                        elif 480 <= mouseX <= 520 and 420 <= mouseY <= 450:
                            if self.page != "delete":
                                self.page = "delete"
                            elif self.page == "delete":
                                self.page = "game"
                        #
                        if self.page in ["mouseIsAttackerA", "mouseIsAttackerB"]:
                            self.placeAttacker(mouseX, mouseY, self.page)
                        elif self.page == "delete":
                            self.removeAttacker(mouseX, mouseY)
                        elif self.page == "upgrading":
                            self.upgrade(mouseX, mouseY)
                    #
                    elif self.page == "chooseLevel":
                        self.chooseLevelControl(mouseX, mouseY)
                    elif self.page in ["levelEdit", "LEblock", "LEclear"]:
                        self.levelEditMouseControl(mouseX, mouseY)
                        
                elif event.type == KEYDOWN:
                    if event.key == K_s:   #godly deletes the first one
                        if self.page == "game":
                            self.MonsterAList = self.MonsterAList[1:]
                    elif event.key == K_LEFT:
                        if self.page in ["levelEdit", "LEblock", "LEclear"]:
                            self.levelEditKeyControl("left")
                    elif event.key == K_RIGHT:
                        if self.page == "levelEdit":
                            self.levelEditKeyControl("right")
                    elif event.key == K_UP:
                        if self.page == "levelEdit":
                            self.levelEditKeyControl("up")
                    elif event.key == K_DOWN:
                        if self.page == "levelEdit":
                            self.levelEditKeyControl("down")
                    elif event.key == K_ESCAPE:  #look at here when writing help page
                        if self.page == "helpPage":
                            self.page = "welcome"
                        elif self.page == "chooseLevel":
                            self.page = "welcome"
                        elif self.page == "LEblock":
                            self.page = "levelEdit"
                        elif self.page == "editIllegal":
                            self.levelEditKeyControl("escape")
                        elif self.page in ["game", "mouseIsAttackerA", "mouseIsAttackerB", "delete", "upgrading"]:
                            self.page = "chooseLevel"
                        elif self.page == "highScore":
                            self.page = "welcome"
                    elif event.key == K_p:
                        if self.page in ["game", "mouseIsAttackerA", "mouseIsAttackerB", "delete", "upgrading"]:
                            self.gamePause = not self.gamePause
                    elif event.key == K_r:
                        if self.page in ["game", "mouseIsAttackerA", "mouseIsAttackerB", "delete", "upgrading"]:
                            self.restart()  #need to take in level and stuff
                    elif event.key == K_n:
                        if self.page in ["game", "mouseIsAttackerA", "mouseIsAttackerB", "delete", "upgrading"]:
                            if self.win == True:
                                self.nextStage()


            if self.page in  ["game", "mouseIsAttackerA", "mouseIsAttackerB", "delete", "upgrading"]:
                if not self.gamePause:
                    for monsterList in [self.MonsterAList, self.MonsterBList]:
                        self.MonsterMove(self.direction, monsterList)  #AttackerB attack in this place
                        self.monsterUpdate(monsterList)
                    self.AttackerAttack(self.AttackerAList)
                    #self.AttackerBAttack()
                    self.BulletUpdate()
                    self.winLoseUpdate()
                    if self.survivalMode == True:
                        self.survivalModeUpdate()
                    if self.win == True:
                        if self.recordTime == None:  #only record once
                            self.recordTime = time.time() - self.gameStartTime
                            self.changeHighScore()
            elif self.page == "chooseLevel":
                self.chooseLevelUpdate()
            elif self.page == "welcome":
                self.welcomeControl(mouseX, mouseY, event)

            #####
            #the draw part
            if self.page == "helpPage":
                self.drawHelpPage()
            if self.page == "welcome":
                self.drawWelcome()
            if self.page == "highScore":
                self.drawHighScore()
            if self.page in ["levelEdit", "LEblock", "LEclear", "editIllegal"]:
                self.drawlevelEdit(mouseX, mouseY)
            if self.page == "chooseLevel":
                self.drawchooseLevel(mouseX, mouseY)
            if self.page in ["game", "mouseIsAttackerA", "mouseIsAttackerB", "delete", "upgrading"]:
                self.drawGamePage(mouseX, mouseY)
                #
                if self.page in ["game",  "delete"]:  #eliminated mouseIsAttacker A,B
                    if self.win == None:
                        self.showSpec(mouseX, mouseY)  #don't know why it not work
                elif self.page in ["mouseIsAttackerA", "mouseIsAttackerB"]:
                    if self.win == None:
                        self.showRange(mouseX, mouseY, self.page)
                elif self.page == "upgrading":
                    if self.win == None:
                        self.showUpgradeCost(mouseX, mouseY)
            clock.tick(60)  #this is for fraps
            pygame.display.update()

TowerDefense().run()
