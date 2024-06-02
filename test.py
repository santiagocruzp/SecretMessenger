import random
import time
import turtle

turtle.tracer(1000,0)
turtle.setworldcoordinates(0,0,700,700)
turtle.hideturtle()

def drawBranch(startPosition, direction, branchLength):
    # get pesudorandom numbers for the branch properties
    seed = 0
    random.seed(seed)
    LEFT_ANGLE = random.randint(10, 30)
    LEFT_DECREASE = random.randint(8, 15)
    RIGHT_ANGLE = random.randint(10, 30)
    RIGHT_DECREASE = random.randint(8, 15)
    START_LENGTH = random.randint(80, 120)
    if branchLength < 5:
        #BASE CASE
        return

    # go to the starting point and direction
    turtle.penup()
    turtle.goto(startPosition)
    turtle.setheading(direction)

    # draw the branch (thickness is 1/7 the length)
    turtle.pendown()
    turtle.pensize(max(branchLength/7.0,1))
    turtle.forward(branchLength)

    # Record the position of the branch's end
    endposition = turtle.position()
    leftDirection = direction + LEFT_ANGLE
    leftBranchLength = branchLength - LEFT_DECREASE
    rightDirection = direction + RIGHT_ANGLE
    rightBranchLength = branchLength - RIGHT_DECREASE

    # RECURSIVE CASE
    drawBranch(endposition, leftDirection, leftBranchLength)
    drawBranch(endposition, rightDirection, rightBranchLength)

    while True:
        turtle.clear()
        turtle.penup()
        turtle.goto(10,10)
        turtle.write('Seed: %s' % seed)   # Write out the seed number

        # Draw the tree
        drawBranch((350,10),90, START_LENGTH)
        turtle.update()
        time.sleep(2)

        seed += 1
