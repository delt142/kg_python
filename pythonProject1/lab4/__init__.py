
import pygame  # Импортируем библиотеку Pygame для работы с графикой и событиями
from pygame.locals import *  # Импортируем все локальные константы из Pygame, такие как клавиши и события
from OpenGL.GL import *  # Импортируем функции OpenGL для отрисовки 3D-объектов
from OpenGL.GLU import *  # Импортируем утилиты OpenGL для работы с перспективой и другими функциями
import numpy as np  # Импортируем NumPy для работы с массивами и матрицами

# Определение вершин и граней куба
vertices = [
    [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1],  # Задание вершин задней грани
    [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1]  # Задание вершин передней грани
]
edges = [  # Определение рёбер куба
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]
faces = [  # Определение граней куба
    (0, 1, 2, 3), (3, 2, 6, 7),
    (7, 6, 5, 4), (4, 5, 1, 0),
    (1, 5, 6, 2), (4, 0, 3, 7)
]
colors = [  # Определение цветов для каждой грани куба
    (1, 0, 0), (0, 1, 0), (0, 0, 1),
    (1, 1, 0), (1, 0, 1), (0, 1, 1)
]

# Функция для создания матрицы трансляции
def create_translation_matrix(tx, ty, tz):
    return np.array([  # Возвращаем 4x4 матрицу трансляции
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])

# Функция для создания матрицы масштабирования
def create_scaling_matrix(sx, sy, sz):
    return np.array([  # Возвращаем 4x4 матрицу масштабирования
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ])

# Функция для создания матрицы вращения
def create_rotation_matrix(angle, ax, ay, az):
    rad = np.radians(angle)  # Преобразование угла из градусов в радианы
    c, s = np.cos(rad), np.sin(rad)  # Вычисление косинуса и синуса угла
    return np.array([  # Возвращаем 4x4 матрицу вращения
        [c + (1 - c) * ax * ax, (1 - c) * ax * ay - s * az, (1 - c) * ax * az + s * ay, 0],
        [(1 - c) * ay * ax + s * az, c + (1 - c) * ay * ay, (1 - c) * ay * az - s * ax, 0],
        [(1 - c) * az * ax - s * ay, (1 - c) * az * ay + s * ax, c + (1 - c) * az * az, 0],
        [0, 0, 0, 1]
    ])

# Функция для рисования координатных осей
def draw_axes():
    glBegin(GL_LINES)  # Начинаем рисование линий
    # Ось X (красный)
    glColor3fv((1, 0, 0))  # Устанавливаем цвет для оси X
    glVertex3f(-10, 0, 0)  # Начало линии оси X
    glVertex3f(10, 0, 0)   # Конец линии оси X
    # Ось Y (зеленый)
    glColor3fv((0, 1, 0))  # Устанавливаем цвет для оси Y
    glVertex3f(0, -10, 0)  # Начало линии оси Y
    glVertex3f(0, 10, 0)   # Конец линии оси Y
    # Ось Z (синий)
    glColor3fv((0, 0, 1))  # Устанавливаем цвет для оси Z
    glVertex3f(0, 0, -10)  # Начало линии оси Z
    glVertex3f(0, 0, 10)   # Конец линии оси Z
    glEnd()  # Завершаем рисование линий

# Функция для рисования куба с трансформацией
def draw_cuboid(scaling, position, rotation):
    # Создание матриц трансформации
    translation_matrix = create_translation_matrix(*position)  # Создание матрицы трансляции
    scaling_matrix = create_scaling_matrix(*scaling)  # Создание матрицы масштабирования
    rotation_x_matrix = create_rotation_matrix(rotation[0], 1, 0, 0)  # Вращение вокруг оси X
    rotation_y_matrix = create_rotation_matrix(rotation[1], 0, 1, 0)  # Вращение вокруг оси Y
    rotation_z_matrix = create_rotation_matrix(rotation[2], 0, 0, 1)  # Вращение вокруг оси Z

    # Комбинирование матриц в порядке: масштабирование, вращение, затем трансляция
    transformation_matrix = np.matmul(translation_matrix,  # Применяем трансформации в заданном порядке
                                      np.matmul(rotation_z_matrix, np.matmul(rotation_y_matrix, np.matmul(rotation_x_matrix, scaling_matrix))))

    glPushMatrix()  # Сохраняем текущую матрицу
    glMultMatrixf(transformation_matrix.T)  # Умножаем текущую матрицу на преобразовательную

    # Рисуем куб
    glEnable(GL_DEPTH_TEST)  # Включаем тест глубины для правильного отображения
    glBegin(GL_QUADS)  # Начинаем рисование квадратов для граней куба
    for i, face in enumerate(faces):  # Для каждой грани
        glColor3fv(colors[i])  # Устанавливаем цвет для грани
        for vertex in face:  # Для каждой вершины грани
            glVertex3fv(vertices[vertex])  # Устанавливаем координату вершины
    glEnd()  # Завершаем рисование граней

    glBegin(GL_LINES)  # Начинаем рисование рёбер
    for edge in edges:  # Для каждого ребра
        for vertex in edge:  # Для каждой вершины ребра
            glVertex3fv(vertices[vertex])  # Устанавливаем координату вершины
    glEnd()  # Завершаем рисование рёбер

    glPopMatrix()  # Восстанавливаем предыдущую матрицу

# Основная функция программы
def main():
    pygame.init()  # Инициализация Pygame
    display = (1620-200, 780-150)  # Устанавливаем размер окна
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)  # Создаем окно с двойной буферизацией и OpenGL
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)  # Устанавливаем перспективу
    glTranslatef(0.0, 0.0, -5)  # Сдвигаем камеру по оси Z

    # Инициализация параметров куба
    position = [0, 0, 0]  # Начальная позиция
    rotation = [0, 0, 0]  # Начальный угол поворота
    scaling = [1, 1, 1]  # Начальный масштаб

    while True:  # Главный цикл программы
        for event in pygame.event.get():  # Обработка событий
            if event.type == pygame.QUIT:  # Если событие выхода
                pygame.quit()  # Закрываем Pygame
                return  # Выходим из функции
            if event.type == KEYDOWN:  # Если нажата клавиша
                # Управление вращением
                if event.key == K_u: rotation[0] += 5  # Вращение Х
                if event.key == K_j: rotation[0] -= 5  # Вращение Х
                if event.key == K_i: rotation[1] += 5  # Вращение У
                if event.key == K_k: rotation[1] -= 5  # Вращение У
                if event.key == K_o: rotation[2] += 5  # Вращение Z
                if event.key == K_l: rotation[2] -= 5  # Вращение Z
                # Управление перемещением
                if event.key == K_w: position[1] += 0.1  # Перемещение вверх
                if event.key == K_s: position[1] -= 0.1  # Перемещение вниз
                if event.key == K_a: position[0] -= 0.1  # Перемещение влево
                if event.key == K_d: position[0] += 0.1  # Перемещение вправо
                if event.key == K_q: position[2] += 0.1  # Перемещение вперед
                if event.key == K_e: position[2] -= 0.1  # Перемещение назад
                # Управление масштабированием
                if event.key == K_r: scaling[0] += 0.1  # Увеличение масштаба по X
                if event.key == K_f: scaling[0] -= 0.1  # Уменьшение масштаба по X
                if event.key == K_t: scaling[1] += 0.1  # Увеличение масштаба по Y
                if event.key == K_g: scaling[1] -= 0.1  # Уменьшение масштаба по Y
                if event.key == K_y: scaling[2] += 0.1  # Увеличение масштаба по Z
                if event.key == K_h: scaling[2] -= 0.1  # Уменьшение масштаба по Z

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Очистка цветового и глубинного буферов
        draw_axes()  # Рисуем координатные оси
        draw_cuboid(scaling, position, rotation)  # Рисуем куб с текущими трансформациями
        pygame.display.flip()  # Обновление окна с новым изображением
        pygame.time.wait(10)  # Задержка для плавности анимации

if __name__ == "__main__":  # Проверка на запуск скрипта напрямую
    main()  # Запускаем основную функцию
