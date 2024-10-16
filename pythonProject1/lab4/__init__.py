import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


vertices = [
    [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1],
    [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1]
]
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]
faces = [
    (0, 1, 2, 3), (3, 2, 6, 7),
    (7, 6, 5, 4), (4, 5, 1, 0),
    (1, 5, 6, 2), (4, 0, 3, 7)
]
colors = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),#задняя часть лево перед
    (1, 0, 1), (16, 10, 100), (1, 1, 1)#право низ  вверх
]


def create_translation_matrix(tx, ty, tz):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])


def create_scaling_matrix(sx, sy, sz):
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ])

def create_rotation_matrix(angle, ax, ay, az):
    rad = np.radians(angle)
    c, s = np.cos(rad), np.sin(rad)
    return np.array([
        [c + (1 - c) * ax * ax, (1 - c) * ax * ay - s * az, (1 - c) * ax * az + s * ay, 0],
        [(1 - c) * ay * ax + s * az, c + (1 - c) * ay * ay, (1 - c) * ay * az - s * ax, 0],
        [(1 - c) * az * ax - s * ay, (1 - c) * az * ay + s * ax, c + (1 - c) * az * az, 0],
        [0, 0, 0, 1]
    ])

def draw_axes():
    glBegin(GL_LINES)
    glColor3fv((1, 0, 0))
    glVertex3f(-10, 0, 0)
    glVertex3f(10, 0, 0)
    glColor3fv((0, 1, 0))
    glVertex3f(0, -10, 0)
    glVertex3f(0, 10, 0)
    glColor3fv((0, 0, 1))
    glVertex3f(0, 0, -10)
    glVertex3f(0, 0, 10)
    glEnd()


def create_perspective_matrix(fov, aspect_ratio, near, far):
    """Создаем ручную матрицу перспективы"""
    f = 1.0 / np.tan(np.radians(fov) / 2)
    return np.array([
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0]
    ], dtype=float)
# def draw_cuboid(scaling, position, rotation):
#     translation_matrix = create_translation_matrix(*position)
#     scaling_matrix = create_scaling_matrix(*scaling)
#     rotation_x_matrix = create_rotation_matrix(rotation[0], 1, 0, 0)
#     rotation_y_matrix = create_rotation_matrix(rotation[1], 0, 1, 0)
#     rotation_z_matrix = create_rotation_matrix(rotation[2], 0, 0, 1)
#     transformation_matrix = np.matmul(translation_matrix,
#                                       np.matmul(rotation_z_matrix, np.matmul(rotation_y_matrix, np.matmul(rotation_x_matrix, scaling_matrix))))
#
#     glPushMatrix()
#     glMultMatrixf(transformation_matrix.T)
#     glEnable(GL_DEPTH_TEST)
#     glBegin(GL_QUADS)
#     for i, face in enumerate(faces):
#         glColor3fv(colors[i])
#         for vertex in face:
#             glVertex3fv(vertices[vertex])
#     glEnd()
#
#     glBegin(GL_LINES)
#     for edge in edges:
#         for vertex in edge:
#             glVertex3fv(vertices[vertex])
#     glEnd()
#
#     glPopMatrix()


def draw_cuboid(scaling, position, rotation):
    # Создаем матрицы трансформации
    translation_matrix = create_translation_matrix(*position)
    scaling_matrix = create_scaling_matrix(*scaling)
    rotation_x_matrix = create_rotation_matrix(rotation[0], 1, 0, 0)
    rotation_y_matrix = create_rotation_matrix(rotation[1], 0, 1, 0)
    rotation_z_matrix = create_rotation_matrix(rotation[2], 0, 0, 1)

    # Комбинирование матриц
    transformation_matrix = translation_matrix @ rotation_z_matrix @ rotation_y_matrix @ rotation_x_matrix @ scaling_matrix

    # Применение перспективного преобразования
    aspect_ratio = 800 / 600  # Например, ширина / высота окна
    perspective_matrix = create_perspective_matrix(45, aspect_ratio, 0.1, 100)

    glPushMatrix()
    glMultMatrixf(perspective_matrix.T)  # Применяем матрицу перспективы
    glMultMatrixf(transformation_matrix.T)  # Применяем комбинированную матрицу трансформации
    glEnable(GL_DEPTH_TEST)

    # Вычисление и рисование куба
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        # Рассчитаем нормали для грани
        v1 = np.array(vertices[face[1]], dtype=float) - np.array(vertices[face[0]], dtype=float)
        v2 = np.array(vertices[face[2]], dtype=float) - np.array(vertices[face[0]], dtype=float)
        normal = np.cross(v1, v2)
        normal /= np.linalg.norm(normal)  # Нормализация нормали

        # Проверка видимости грани
        camera_direction = np.array([0.0, 0.0, -1.0], dtype=float)  # Направление взгляда камеры
        if np.dot(normal, camera_direction) < 0:  # Грань видима
            glColor3fv(colors[i])  # Задаем цвет
            for vertex in face:
                glVertex3fv(vertices[vertex])  # Рисуем вершины
    glEnd()

    # Рисуем линии
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    glPopMatrix()


def main():
    pygame.init()
    display = (1620-200, 780-150)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    position = [0, 0, 0]
    rotation = [0, 0, 0]
    scaling = [1, 1, 1]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == KEYDOWN:
                if event.key == K_u: rotation[0] += 5
                if event.key == K_j: rotation[0] -= 5
                if event.key == K_i: rotation[1] += 5
                if event.key == K_k: rotation[1] -= 5
                if event.key == K_o: rotation[2] += 5
                if event.key == K_l: rotation[2] -= 5
                if event.key == K_w: position[1] += 0.1
                if event.key == K_s: position[1] -= 0.1
                if event.key == K_a: position[0] -= 0.1
                if event.key == K_d: position[0] += 0.1
                if event.key == K_q: position[2] += 0.1
                if event.key == K_e: position[2] -= 0.1
                if event.key == K_r: scaling[0] += 0.1
                if event.key == K_f: scaling[0] -= 0.1
                if event.key == K_t: scaling[1] += 0.1
                if event.key == K_g: scaling[1] -= 0.1
                if event.key == K_y: scaling[2] += 0.1
                if event.key == K_h: scaling[2] -= 0.1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_axes()
        draw_cuboid(scaling, position, rotation)
        pygame.display.flip()
        pygame.time.wait(10)
if __name__ == "__main__":
    main()
