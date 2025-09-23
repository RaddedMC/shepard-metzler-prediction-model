import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

### Defined values ###
cube_positions = [
    (0,0,0),
    (2,0,0),
    (4,0,0),
    (4,2,0),
    (4,4,0),
]

# Define a cube (8 vertices)
vertices = [
    [1, 1, -1],
    [1, -1, -1],
    [-1, -1, -1],
    [-1, 1, -1],
    [1, 1, 1],
    [1, -1, 1],
    [-1, -1, 1],
    [-1, 1, 1]
]

edges = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]

def draw_cube(position=(0,0,0)):
    """Draw a cube translated to the given position"""
    glPushMatrix()
    glTranslatef(*position)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    glPopMatrix()

def render_shape(cubes, angle=(30,30)):
    """Render a shape made from cubes at a given angle, with mouse control"""
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -20)

    clock = pygame.time.Clock()
    running = True

    rot_x, rot_y = angle
    dragging = False
    last_mouse_pos = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    last_mouse_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging and last_mouse_pos:
                    x, y = pygame.mouse.get_pos()
                    dx = x - last_mouse_pos[0]
                    dy = y - last_mouse_pos[1]
                    rot_x += dy * 0.5
                    rot_y += dx * 0.5
                    last_mouse_pos = (x, y)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        # Draw all cubes in the shape
        for cube_pos in cubes:
            draw_cube(cube_pos)

        glPopMatrix()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

# Example: build a shape (like a "stair step" of cubes)
anglex = 40
render_shape(cube_positions, angle=(anglex,45))