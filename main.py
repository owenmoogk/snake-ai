import pygame
import sys
import random
from random import randint
import pickle
import os

# config var
windowWidth = 1000
windowHeight = 1000
clock = pygame.time.Clock()

# display
screen = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption('Snake')

#colors
black = (0,0,0)
green = (0,255,0)
red = (255,0,0)

# fonts
pygame.font.init()
font = pygame.font.SysFont("comicsans", 50)

# game
score = 0
gridSize = 40
gameSpeed = 7
gridHeight = windowHeight / gridSize
gridWidth = windowWidth / gridSize
snakeSquares = [] # keeps the snake square objects


class snake:
    def __init__(self, x, y, direction):
        self.x = x * gridSize
        self.y = y * gridSize
        self.direction = direction
    
    def drawSquare(self):
        pygame.draw.rect(screen, green, (self.x+1,self.y+1,gridSize-2, gridSize-2))

    def move(self):
        if self.direction == "left":
            self.x -= gridSize
        elif self.direction == "right":
            self.x += gridSize
        elif self.direction == "up":
            self.y -= gridSize
        elif self.direction == "down":
            self.y += gridSize
        if self.y < 0 or self.y >= windowHeight or self.x < 0 or self.x >= windowWidth:
            return(True)
        
    def changeDirection(self, direction):
        if self.direction == "up" and direction == "down":
            return
        elif self.direction == "down" and direction == "up":
            return
        elif self.direction == "left" and direction == "right":
            return
        elif self.direction == "right" and direction == "left":
            return
        else:
            self.direction = direction

class food:
    def __init__(self):
        self.spawnFood()
    
    def drawFood(self):
        pygame.draw.rect(screen, red, (self.x+1,self.y+1, gridSize-2, gridSize-2))
    
    def spawnFood(self):
        improper = True
        while improper:
            self.x = randint(0,gridWidth-1) * gridSize
            self.y = randint(0,gridHeight-1) * gridSize
            improper = False
            for i in snakeSquares:
                if self.x == i.x and self.y == i.y:
                    improper = True
                    break

def showScore(score):
    score_label = font.render("Score: " + str(score),1,(255,255,255))
    screen.blit(score_label, (10, 10))

running = True

while running:

    playing = True
    backlog = []
    apple = food()
    apple.spawnFood()
    snakeSquares = [] # keeps the snake square objects
    snakeSquares.append(snake(4,round(windowHeight/gridSize/2),"right"))
    length = 1 # keeps the length of the snake

    while playing:
        clock.tick(gameSpeed)
        pygame.draw.rect(screen, black, (0,0,windowWidth, windowHeight))

        # running thru events
        events = pygame.event.get()
        for event in events:
            # if x button pressed stop just break out of these loops
            if event.type == pygame.QUIT:
                running = False
                playing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    backlog.append("up")
                elif event.key == pygame.K_DOWN:
                    backlog.append("down")
                elif event.key == pygame.K_LEFT:
                    backlog.append("left")
                elif event.key == pygame.K_RIGHT:
                    backlog.append("right")
        
        # if backlog has elements on it, then execute the first (every loop)
        if len(backlog) > 0:
            snakeSquares[0].changeDirection(backlog[0])
            del(backlog[0])
        
        if len(snakeSquares) < length:
            snakeSquares.append(snake(0,0,"left")) # the left doesnt matter

        # "moving" the body
        for i in range(len(snakeSquares)-1,0,-1):
            snakeSquares[i].x = snakeSquares[i-1].x
            snakeSquares[i].y = snakeSquares[i-1].y
        
        # moving the head
        isDead = snakeSquares[0].move()
        if isDead:
            playing = False

        # collision detection
        if snakeSquares[0].x == apple.x and snakeSquares[0].y == apple.y:
            apple.spawnFood()
            length += 1
        for i in range(1, len(snakeSquares)):
            if snakeSquares[0].x == snakeSquares[i].x and snakeSquares[0].y == snakeSquares[i].y:
                playing = False

        # drawing
        apple.drawFood()
        for i in snakeSquares:
            i.drawSquare()

        # update display
        pygame.display.update()