import pygame  # Импортируем библиотеку Pygame для работы с окнами и событиями
from pygame.locals import *  # Импортируем константы для обработки событий Pygame
from OpenGL.GL import *  # Импортируем функции OpenGL для рисования
from OpenGL.GLU import *  # Импортируем GLU для дополнительных функций OpenGL
import numpy as np  # Импортируем NumPy для работы с массивами и матрицами

# Определяем вершины куба
vertices = [
    [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1],
    [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1]
]

# Определяем рёбра куба
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

# Определяем грани (лицевые поверхности) куба
faces = [
    (0, 1, 2, 3), (3, 2, 6, 7),
    (7, 6, 5, 4), (4, 5, 1, 0),
    (1, 5, 6, 2), (4, 0, 3, 7)
]

# Определяем цвета для каждой грани куба
colors = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),  # Красный, зелёный, синий
    (1, 0, 1), (1, 1, 0), (1, 1, 1)   # Магента, жёлтый, белый
]

# Функция создания матрицы трансляции
def create_translation_matrix(tx, ty, tz):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])

# Функция создания матрицы масштабирования
def create_scaling_matrix(sx, sy, sz):
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ])

# Функция создания матрицы вращения
def create_rotation_matrix(angle, ax, ay, az):
    rad = np.radians(angle)  # Преобразуем угол в радианы
    c, s = np.cos(rad), np.sin(rad)  # Вычисляем косинус и синус
    return np.array([
        [c + (1 - c) * ax * ax, (1 - c) * ax * ay - s * az, (1 - c) * ax * az + s * ay, 0],
        [(1 - c) * ay * ax + s * az, c + (1 - c) * ay * ay, (1 - c) * ay * az - s * ax, 0],
        [(1 - c) * az * ax - s * ay, (1 - c) * az * ay + s * ax, c + (1 - c) * az * az, 0],
        [0, 0, 0, 1]
    ])

# Функция рисования координатных осей
def draw_axes():
    glBegin(GL_LINES)  # Начинаем рисовать линии
    glColor3fv((1, 0, 0))  # Устанавливаем цвет оси X (красный)
    glVertex3f(-10, 0, 0)  # Начало оси X
    glVertex3f(10, 0, 0)   # Конец оси X
    glColor3fv((0, 1, 0))  # Устанавливаем цвет оси Y (зелёный)
    glVertex3f(0, -10, 0)  # Начало оси Y
    glVertex3f(0, 10, 0)   # Конец оси Y
    glColor3fv((0, 0, 1))  # Устанавливаем цвет оси Z (синий)
    glVertex3f(0, 0, -10)  # Начало оси Z
    glVertex3f(0, 0, 10)   # Конец оси Z
    glEnd()  # Заканчиваем рисование


# def create_perspective_matrix(fov, aspect_ratio, near, far):
#     """Создаем ручную матрицу перспективы"""
#     f = 1.0 / np.tan(np.radians(fov) / 2)  # Вычисляем фактор фокусного расстояния
#     return np.array([
#         [f / aspect_ratio, 0, 0, 0],  # Матрица масштабирования по ширине
#         [0, f, 0, 0],  # Матрица масштабирования по высоте
#         [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],  # Матрица перспективного проецирования
#         [0, 0, -1, 0]  # Установка направления Z
#     ], dtype=float)  # Возвращаем матрицу с типом float


# Функция рисования куба
def draw_cuboid(scaling, position, rotation):
    # Создаём матрицы для трансляции, масштабирования и вращения
    translation_matrix = create_translation_matrix(*position)
    scaling_matrix = create_scaling_matrix(*scaling)
    rotation_x_matrix = create_rotation_matrix(rotation[0], 1, 0, 0)
    rotation_y_matrix = create_rotation_matrix(rotation[1], 0, 1, 0)
    rotation_z_matrix = create_rotation_matrix(rotation[2], 0, 0, 1)

    # Объединяем все матрицы в одну трансформацию
    transformation_matrix = np.matmul(translation_matrix,
                                      np.matmul(rotation_z_matrix, np.matmul(rotation_y_matrix,
                                                                             np.matmul(rotation_x_matrix,
                                                                                       scaling_matrix))))

    glPushMatrix()  # Запоминаем текущую матрицу
    glMultMatrixf(transformation_matrix.T)  # Применяем трансформацию
    glEnable(GL_DEPTH_TEST)  # Включаем тест глубины для правильного отображения
    glBegin(GL_QUADS)  # Начинаем рисовать грани куба
    for i, face in enumerate(faces):
        glColor3fv(colors[i])  # Устанавливаем цвет для текущей грани
        for vertex in face:
            glVertex3fv(vertices[vertex])  # Рисуем вершины грани
    glEnd()

    glBegin(GL_LINES)  # Начинаем рисовать рёбра куба
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])  # Рисуем рёбра
    glEnd()

    glPopMatrix()  # Восстанавливаем предыдущую матрицу


# def draw_cuboid(scaling, position, rotation):
#     # Создаем матрицы трансформации
#     translation_matrix = create_translation_matrix(*position)  # Матрица трансляции
#     scaling_matrix = create_scaling_matrix(*scaling)  # Матрица масштабирования
#     rotation_x_matrix = create_rotation_matrix(rotation[0], 1, 0, 0)  # Матрица вращения вокруг оси X
#     rotation_y_matrix = create_rotation_matrix(rotation[1], 0, 1, 0)  # Матрица вращения вокруг оси Y
#     rotation_z_matrix = create_rotation_matrix(rotation[2], 0, 0, 1)  # Матрица вращения вокруг оси Z
#
#     # Комбинирование матриц
#     transformation_matrix = translation_matrix @ rotation_z_matrix @ rotation_y_matrix @ rotation_x_matrix @ scaling_matrix
#     # Создаем комбинированную матрицу трансформации с помощью матричного умножения
#
#     # Применение перспективного преобразования
#     aspect_ratio = 800 / 600  # Определение соотношения сторон окна
#     perspective_matrix = create_perspective_matrix(45, aspect_ratio, 0.1, 100)  # Создание матрицы перспективы
#
#     glPushMatrix()  # Сохраняем текущую матрицу
#     glMultMatrixf(perspective_matrix.T)  # Применяем матрицу перспективы
#     glMultMatrixf(transformation_matrix.T)  # Применяем комбинированную матрицу трансформации
#     glEnable(GL_DEPTH_TEST)  # Включаем тест глубины для корректного отображения
#
#     # Вычисление и рисование куба
#     glBegin(GL_QUADS)  # Начинаем рисование граней
#     for i, face in enumerate(faces):  # Проходим по всем граням
#         # Рассчитаем нормали для грани
#         v1 = np.array(vertices[face[1]], dtype=float) - np.array(vertices[face[0]], dtype=float)  # Вектор 1 грани
#         v2 = np.array(vertices[face[2]], dtype=float) - np.array(vertices[face[0]], dtype=float)  # Вектор 2 грани
#         normal = np.cross(v1, v2)  # Вычисляем нормаль к грани
#         normal /= np.linalg.norm(normal)  # Нормализация нормали для единичной длины
#
#         # Проверка видимости грани
#         camera_direction = np.array([0.0, 0.0, -1.0], dtype=float)  # Направление взгляда камеры
#         if np.dot(normal, camera_direction) < 0:  # Проверяем, видима ли грань
#             glColor3fv(colors[i])  # Устанавливаем цвет для видимой грани
#             for vertex in face:
#                 glVertex3fv(vertices[vertex])  # Рисуем вершины грани
#     glEnd()  # Заканчиваем рисование граней
#
#     # Рисуем линии
#     glBegin(GL_LINES)  # Начинаем рисовать рёбра
#     for edge in edges:  # Проходим по всем рёбрам
#         for vertex in edge:  # Проходим по вершинам рёбра
#             glVertex3fv(vertices[vertex])  # Рисуем вершины рёбров
#     glEnd()  # Заканчиваем рисование линий
#
#     glPopMatrix()  # Восстанавливаем предыдущую матрицу

# Основная функция
def main():
    pygame.init()  # Инициализируем Pygame
    display = (1620-200, 780-150)  # Определяем размер окна
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)  # Создаём окно для OpenGL
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)  # Устанавливаем перспективу
    glTranslatef(0.0, 0.0, -5)  # Перемещаем сцену по оси Z
    position = [0, 0, 0]  # Начальная позиция
    rotation = [0, 0, 0]  # Начальные углы вращения
    scaling = [1, 1, 1]   # Начальный масштаб

    while True:  # Главный игровой цикл
        for event in pygame.event.get():  # Обработка событий
            if event.type == pygame.QUIT:  # Если закрываем окно
                pygame.quit()  # Завершаем Pygame
                return  # Выходим из функции
            if event.type == KEYDOWN:  # Если нажата клавиша
                # Обработка нажатий для вращения
                if event.key == K_u: rotation[0] += 5
                if event.key == K_j: rotation[0] -= 5
                if event.key == K_i: rotation[1] += 5
                if event.key == K_k: rotation[1] -= 5
                if event.key == K_o: rotation[2] += 5
                if event.key == K_l: rotation[2] -= 5
                # Обработка нажатий для перемещения
                if event.key == K_w: position[1] += 0.1
                if event.key == K_s: position[1] -= 0.1
                if event.key == K_a: position[0] -= 0.1
                if event.key == K_d: position[0] += 0.1
                if event.key == K_q: position[2] += 0.1
                if event.key == K_e: position[2] -= 0.1
                # Обработка нажатий для изменения масштаба
                if event.key == K_r: scaling[0] += 0.1
                if event.key == K_f: scaling[0] -= 0.1
                if event.key == K_t: scaling[1] += 0.1
                if event.key == K_g: scaling[1] -= 0.1
                if event.key == K_y: scaling[2] += 0.1
                if event.key == K_h: scaling[2] -= 0.1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Очищаем буфер цвета и глубины
        draw_axes()  # Рисуем оси
        draw_cuboid(scaling, position, rotation)  # Рисуем куб
        pygame.display.flip()  # Обновляем экран
        pygame.time.wait(10)  # Задержка для контроля частоты кадров

# Запуск основной функции, если это скрипт запускается непосредственно
if __name__ == "__main__":
    main()  # Запуск программы
