import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time

airplane_x, airplane_y = 5, 300
gravity = -.5  # plane
flap_strength = 8
ufo_speed=1
ufo_speed_y=.5

STATE_MENU, STATE_GAME, STATE_EXIT = 0, 1, 2
game_state = STATE_MENU

airplane_height=40
airplane_width=140

ufo_x=780
ufo_y=300
ufo_height=25
ufo_width=70
bullet_height=5
bullet_width=15

ufo_list = []
last_ufo_time = time.time()
score=0
bullet_list = []
count=0
game_over_flag = False


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
NUM_PILLARS = 10
PILLAR_SPACING = 150.0
PILLAR_WIDTH = 10.0
SPEED = 2.0
paused = False


# Pillar positions
pillar_positions = [WINDOW_WIDTH + i * PILLAR_SPACING for i in range(NUM_PILLARS)]
pillar_spaces = [random.randint(50, 100) for _ in range(NUM_PILLARS)]  # Random gaps

def initialize():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

def render_text(x, y, text, color=(1,1,1)):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def display_menu_1():
    glClear(GL_COLOR_BUFFER_BIT)

    render_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, "NEW GAME", (0, 0, 1))
    render_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, "EXIT", (1.0, 0.0, 0.0))
    glFlush()

def display_menu_2():
    global score
    glClear(GL_COLOR_BUFFER_BIT)
    render_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100, "RESUME", (0.2, 0.8, 0.2))
    render_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, "NEW GAME", (0, 0, 1))
    render_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, "EXIT", (1.0, 0.0, 0.0))
    score_text = f"Score: {score}"
    render_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50, score_text, (1.0, 1.0, 0.0))  # Yellow color for score
    glFlush()

def mouse_menu(button, state, x, y):
    global game_state, paused, game_over_flag
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Convert mouse coordinates (GLUT has the origin at the bottom left)
        c_x, c_y = x, WINDOW_HEIGHT - y  # Correct coordinate transformation
        if game_over_flag:
            if 0 <= x <= 100 and 0 <= y <= 100:  # Check if the click is in the top-left corner (100x100 area)
              # Restart the game only if it's game over
                restart_game()
        if game_state == STATE_MENU:  # Main menu
            if WINDOW_WIDTH // 2 - 100 < c_x < WINDOW_WIDTH // 2 + 100:
                if WINDOW_HEIGHT // 2 + 50 < c_y < WINDOW_HEIGHT // 2 + 90:
                    restart_game()
                    game_state = STATE_GAME  # New Game
                elif WINDOW_HEIGHT // 2 < c_y < WINDOW_HEIGHT // 2 + 40:
                    game_state = STATE_EXIT  # Exit
        elif game_state == STATE_GAME and paused:  # Pause menu
            if WINDOW_WIDTH // 2 - 100 < c_x < WINDOW_WIDTH // 2 + 100:
                if WINDOW_HEIGHT // 2 + 100 < c_y < WINDOW_HEIGHT // 2 + 140:
                    paused = False  # Resume game
                    game_state = STATE_GAME
                elif WINDOW_HEIGHT // 2 + 50 < c_y < WINDOW_HEIGHT // 2 + 90:
                    restart_game()
                    game_state = STATE_GAME  # Start New Game

                    paused = False

                elif WINDOW_HEIGHT // 2 < c_y < WINDOW_HEIGHT // 2 + 40:
                    game_state = STATE_EXIT  # Exit game
                    glutLeaveMainLoop()


def restart_game():
    global last_ufo_time,airplane_x, airplane_y, gravity, flap_strength, score, pillar_positions, pillar_spaces, ufo_list, bullet_list, game_over_flag, count, paused

    # Reset game variables
    airplane_x, airplane_y = 5, 300
    gravity = -0.5
    flap_strength = 8

    score = 0
    count = 0
    game_over_flag = False
    last_ufo_time = time.time()

    ufo_list = []


    pillar_positions = [WINDOW_WIDTH + i * PILLAR_SPACING for i in range(NUM_PILLARS)]
    pillar_spaces = [random.randint(50, 100) for _ in range(NUM_PILLARS)]


    bullet_list = []

    paused = False

def draw_restart_button():
    # Set button color to red
    glColor3f(1.0, 0.0, 0.0)

    # Draw a rectangle for the button at a slightly lower position
    x1, y1 = 10, 550  # Bottom-left corner
    x2, y2 = 110, 550  # Bottom-right corner
    x3, y3 = 110, 600  # Top-right corner
    x4, y4 = 10, 600  # Top-left corner

    # Draw the four edges of the rectangle using draw_line
    draw_line(x1, y1, x2, y2)  # Bottom edge
    draw_line(x2, y2, x3, y3)  # Right edge
    draw_line(x3, y3, x4, y4)  # Top edge
    draw_line(x4, y4, x1, y1)  # Left edge

    # Draw button text in white color
    glColor3f(1.0, 1.0, 1.0)  # White color for text
    render_text(30, 570, "Restart")

def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) > abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        elif dx >= 0 and dy < 0:
            return 7
        elif dx < 0 and dy >= 0:
            return 3
        else:
            return 4
    else:
        if dx >= 0 and dy >= 0:
            return 1
        elif dx >= 0 and dy < 0:
            return 6
        elif dx < 0 and dy >= 0:
            return 2
        else:
            return 5

def convert_to_zone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y

def convert_to_original_zone(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y

def draw_line(x1, y1, x2, y2):
    zone = find_zone(x1, y1, x2, y2)
    x1, y1 = convert_to_zone0(x1, y1, zone)
    x2, y2 = convert_to_zone0(x2, y2, zone)

    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    E = 2 * dy
    NE = 2 * (dy - dx)
    x, y = x1, y1

    glBegin(GL_POINTS)
    while x <= x2:
        orig_x, orig_y = convert_to_original_zone(x, y, zone)
        glVertex2f(orig_x, orig_y)
        if d > 0:
            y += 1
            d += NE
        else:
            d += E
        x += 1
    glEnd()



def draw_pillars():

    glColor3f(1.0, 1.0, 1.0)  # White color
    for i, x in enumerate(pillar_positions):
        space = pillar_spaces[i]

        # Top pillar (from top to middle)
        y_top_start = WINDOW_HEIGHT
        y_top_end = (WINDOW_HEIGHT / 2) + space
        draw_line(x, y_top_start, x, y_top_end)

        # Bottom pillar (from bottom to middle)
        y_bottom_start = 0
        y_bottom_end = (WINDOW_HEIGHT / 2) - space
        draw_line(x, y_bottom_start, x, y_bottom_end)


def update_pillars():
    global pillar_positions, pillar_spaces, score
    for i in range(len(pillar_positions)):
        x = pillar_positions[i]
        pillar_positions[i] -= SPEED
        if pillar_positions[i] - x > 20:
            score+=1
            x = pillar_positions[i]
        # Reset pillar to the right if it moves out of view
        if pillar_positions[i] < -PILLAR_WIDTH:
            pillar_positions[i] = WINDOW_WIDTH + PILLAR_SPACING - PILLAR_WIDTH
            pillar_spaces[i] = random.randint(50,100)  # New random gap



###########################################################
def draw_plane():
    global airplane_x, airplane_y

    glColor3f(0, 1.0, 1.0)  #


    draw_line(airplane_x, airplane_y,airplane_x+.001, airplane_y+20)#195, 200, 195.001 , 220
    draw_line(airplane_x+.001, airplane_y+20,airplane_x+10, airplane_y+20)# tail 195.001 , 220, 205 , 220
    draw_line(airplane_x+10, airplane_y+20,airplane_x+30, airplane_y)#,205 , 220, 225 , 200

    draw_line(airplane_x+65, airplane_y,airplane_x+45, airplane_y+20) #,260, 200, 230, 220
    draw_line(airplane_x+85, airplane_y,airplane_x+65, airplane_y+20)# top wing ,280, 200, 230, 220

    draw_line(airplane_x+45, airplane_y+20,airplane_x+65, airplane_y+20)#,240, 220, 260, 220
    draw_line(airplane_x+75, airplane_y,airplane_x+55, airplane_y+20)#,260, 210, 230, 220

    draw_line(airplane_x+135, airplane_y-20,airplane_x+135.001, airplane_y-12)# ,330, 180, 330.001, 188
    draw_line (airplane_x+115, airplane_y,airplane_x+135, airplane_y-12)  #front,310,200,330,188

    draw_line(airplane_x, airplane_y,airplane_x+115, airplane_y)# plane line airplane_x=195 airplane_y=200  310, 200
    draw_line(airplane_x+25, airplane_y-20 ,airplane_x+135, airplane_y-20)#,330, 180



    draw_line(airplane_x+65, airplane_y-10,airplane_x+45, airplane_y-30)#260, 190, 240, 170

    draw_line(airplane_x+85, airplane_y-10,airplane_x+65, airplane_y-30)#  ,280, 190, 260, 170        # bottom wing
    draw_line(airplane_x+65, airplane_y-10,airplane_x+85, airplane_y-10)#,260, 190, 280, 190
    draw_line(airplane_x+45, airplane_y-30,airplane_x+65, airplane_y-30)#,240, 170, 260, 170
    draw_line(airplane_x+55, airplane_y-30,airplane_x+60, airplane_y-25)#,250, 170, 255, 170

    draw_line(airplane_x+25, airplane_y-20,airplane_x+5, airplane_y)#220, 180, 200, 200

def update_plane():
    global gravity,airplane_y

    if 30<airplane_y<WINDOW_HEIGHT:
        airplane_y+=gravity


def midpoint_halfcircle(x_center, y_center, radius):
    points = []
    x = 0
    y = radius
    d = 1 - radius

    while x <= y:
        points.extend([  # Add points to all octants of the circle
            (x_center + x, y_center + y),
            (x_center - x, y_center + y),
            (x_center + y, y_center + x),
            (x_center - y, y_center + x),
        ])
        if d <= 0:
            d += 2 * x + 3
            x += 1
        else:
            d += 2 * (x - y) + 5
            y -= 1
            x += 1
    return points

def draw_halfcircle(x_center, y_center, radius):
    points = midpoint_halfcircle(x_center, y_center, radius)
    glBegin(GL_POINTS)

    for x, y in points:
        glVertex2f(x, y)
    glEnd()

def draw_ufo(ufo_x, ufo_y, color, time_created,ufo_speed_y):

    glColor3f (*color)
    draw_line(ufo_x-25, ufo_y, ufo_x + 25, ufo_y)
    draw_halfcircle(ufo_x,ufo_y,12)

    draw_line(ufo_x - 25, ufo_y, ufo_x -35, ufo_y-5)
    draw_line(ufo_x + 25, ufo_y, ufo_x + 35, ufo_y - 5)
    draw_line( ufo_x -35, ufo_y-5, ufo_x +35, ufo_y - 5)

def show_ufo_animation():
    global last_ufo_time, ufo_x, ufo_y,ufo_speed_y
    current_time = time.time()
    # Create  ufo every 5 seconds

    if current_time - last_ufo_time >= 5:
        color = (0, 1, 0)
        ufo_list.append([ufo_x, ufo_y, color, time.time(),ufo_speed_y])
        last_ufo_time = current_time


def draw_ufo_positions():
    global ufo_list, ufo_speed
    if not game_over_flag:
        if not paused:  # Only update UFO positions when not paused
            for ufo in ufo_list:
                x, y, color, time_created, ufo_speed_y = ufo

                # Bounce UFO vertically between y = 280 and y = 320
                if y >= 320:
                    ufo_speed_y = -abs(ufo_speed_y)  # Move downward
                elif y <= 280:
                    ufo_speed_y = abs(ufo_speed_y)  # Move upward

                y += ufo_speed_y
                ufo[1] = y
                ufo[4] = ufo_speed_y
                ufo[0] -= ufo_speed  # Move UFO leftward

    # Draw UFOs
    for ufo in ufo_list:
        draw_ufo(ufo[0], ufo[1], ufo[2], ufo[3], ufo[4])

def draw_bullet():
    global bullet_list
    glColor3f(1.0,.843, 0.0)
    for fire in bullet_list:
        bullet_x=fire[0]
        bullet_y=fire[1]
        draw_line(bullet_x,bullet_y,bullet_x+10,bullet_y)
        draw_line(bullet_x, bullet_y+3, bullet_x + 10, bullet_y+3)
        #top
        draw_line(bullet_x + 10, bullet_y+3, bullet_x + 13, bullet_y + 1)
        draw_line(bullet_x+10,bullet_y, bullet_x + 13, bullet_y + 1)
        #bottom
        draw_line(bullet_x, bullet_y, bullet_x+.001, bullet_y+3)




def update_bullet():
    global bullet_list,SPEED,ufo_list,score,count
    for bullet in bullet_list:
            bullet[0] += SPEED


    for bullet in bullet_list:
         for ufo in ufo_list:
            if bullet_collides_with_ufo(ufo,bullet):
                count+=1
                score += 1
                bullet_list.remove(bullet)
                if count%2!=0:
                    ufo[2]=(1,0,0)
                else:
                    ufo_list.remove(ufo)


                print("Score:", score)

def bullet_collides_with_ufo(ufo, bullet):
    global bullet_width,bullet_height,ufo_width,ufo_height,ufo_x,ufo_y


    return (ufo[0] < bullet[0] + bullet_width
                and ufo[0] + ufo_width > bullet[0]
                and ufo[1] < bullet[1] + bullet_height
                and ufo[1]+ ufo_height> bullet[1])



def keyboard(key, x, y):
    global flap_strength,airplane_y,airplane_x, paused,game_state
    if key == b' ':
        if airplane_y < (WINDOW_HEIGHT - 30) and not paused and not game_over_flag:
            airplane_y += flap_strength
    elif key == b'\r':

        bullet_list.append([airplane_x+130, airplane_y-20])
    elif key == b'p':
        paused = not paused
        if not paused:  # If unpaused, resume the game
            game_state = STATE_GAME

def check_collision():
    global airplane_x, airplane_y, pillar_positions, pillar_spaces, game_over_flag

    airplane_width = 140
    airplane_height = 20

    for i, pillar_x in enumerate(pillar_positions):
        space = pillar_spaces[i]
        pillar_top_start = (WINDOW_HEIGHT / 2) + space
        pillar_bottom_end = (WINDOW_HEIGHT / 2) - space

        # Check if airplane overlaps with pillar
        if (pillar_x < airplane_x + airplane_width and
                pillar_x + PILLAR_WIDTH > airplane_x and
                pillar_top_start < airplane_y + airplane_height and
                pillar_top_start + (WINDOW_HEIGHT - pillar_top_start) > airplane_y):

            game_over_flag = True
            print("game over")

        if (pillar_x < airplane_x + airplane_width and
                pillar_x + PILLAR_WIDTH > airplane_x and
                pillar_bottom_end < airplane_y + airplane_height and
                pillar_bottom_end + (20) > airplane_y):

            game_over_flag = True
            print("game over")


    # Airplane and UFO collision
    for ufo in ufo_list:
        ufo_x, ufo_y, _, _, _ = ufo
        if (ufo_x < airplane_x + airplane_width and
                ufo_x + ufo_width > airplane_x and
                ufo_y < airplane_y + airplane_height and
                ufo_y + ufo_height > airplane_y):
            game_over_flag = True
            print("game over")

def display():

        global game_state, STATE_MENU, STATE_GAME, STATE_EXIT,  paused

        if game_state == STATE_MENU:
            display_menu_1()
        elif paused:
            display_menu_2()
        # Show the pause menu
        elif game_state == STATE_GAME:
            display_game()
        elif game_state == STATE_EXIT:
            glutLeaveMainLoop()

def display_game():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    draw_pillars()
    draw_ufo_positions()
    draw_bullet()
    draw_plane()
    if game_over_flag:
        glColor3f(1.0, 0.0, 0.0)  # Red color for "GAME OVER"

        # Approximate centering for text, shifted slightly upwards
        text_width = 150  # Adjust based on the perceived width of "GAME OVER"
        text_height = 10  # Adjust for text height
        vertical_offset = 50  # Move the text up by 50 units (adjust as needed)
        game_over_x = (WINDOW_WIDTH / 2) - (text_width / 2)
        game_over_y = (WINDOW_HEIGHT / 2) - (text_height / 2) + vertical_offset
        render_text(game_over_x, game_over_y, "GAME OVER", (1,0,0))

        # Display total score below "GAME OVER"
        score_text = f"TOTAL SCORE: {score}"
        score_offset = 30  # Space between "GAME OVER" and score
        render_text(game_over_x, game_over_y - score_offset, score_text, (0,0,1))
        draw_restart_button()
    glutSwapBuffers()



def timer(value):
    if not game_over_flag and not paused:
        update_pillars()
        update_plane()
        update_bullet()
        check_collision()
        draw_ufo_positions()
        show_ufo_animation()
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  # 16 ms ~ 60 FPS

# Initialize and start the main loop

glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
glutCreateWindow(b"Menu and Game")
initialize()

glutDisplayFunc(display)
glutMouseFunc(mouse_menu)
glutKeyboardFunc(keyboard)
glutTimerFunc(16, timer, 0)
glutMainLoop()


