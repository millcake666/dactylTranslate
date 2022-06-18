# импортируем библиотеки
import cv2
import mediapipe as mp
from time import time


def find_dist(a, b):  # a - first vector [list], b - second vector [list]
    return sum((int(b[i]) - int(a[i])) ** 2 for i in range(len(a))) ** 0.5


def find_match(vect):   # vect - сравниваемый вектор, return sign
    if len(vect) != 42: return '0'

    _txt = list(i.replace('\n', '').replace(';', '') for i in open('hand_vectors.txt', 'r').readlines())
    vect_base = []

    for v in _txt:
        s = v.split(':')
        vect_base.append(s[0])
        vect_base.append(list(int(i) for i in s[1].split(',')))

    minim = 9999999999
    sign_vect = ''
    for i in range(0, len(vect_base), 2):
        # print(vect_base[i], vect_base[i+1])
        d = find_dist(vect, vect_base[i+1])
        print(vect_base[i], ' - ', d)
        if d < minim:
            minim = d
            sign_vect = vect_base[i]

    return sign_vect


# классы и переменные
cap = cv2.VideoCapture(1)  # захват изображения
mpHands = mp.solutions.hands  # класс для построения связи между опорными точками
hands = mpHands.Hands()  # класс для нахождения опорных точек руки
mpDraw = mp.solutions.drawing_utils  # используется для отображения результатов
mp_drawing_styles = mp.solutions.drawing_styles
cTime = 0  # начальный момент времени для фпс
pTime = 0  # конечный момент времени для фпс
zeroX, zeroY = 0, 0  # храниение координат 0 точки (опорной)

text_timer = time()
text = ''
text_delay = 3
sig, old_sig = 'a', 'b'

# начало функции обработки
while True:
    # print('--------')
    success, img = cap.read()  # получаем кадр
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # конвертируем из BGR в RGB
    results = hands.process(imgRGB)  # находим опорные точки
    # print('res: ', results.multi_hand_landmarks)
    _res = results.multi_hand_landmarks  # список рук, точек и координат соответствен

    if _res:  # если нашли руку в кадре

        if len(_res) > 1:
            cv2.putText(img, "В кадре должна быть только одна рука!", (100, 600), cv2.FONT_HERSHEY_COMPLEX,
                        1.5, (0, 0, 255), 2)
            cv2.imshow("Image", img)  # выводим кадр
            cv2.waitKey(1)
            continue

        hand_vector = []  # вектор руки
        # print('----------count of hands: {}-----------'.format(len(res)))
        for handlms in _res:  # пробегаемся для каждой найденной руки
            # handlms - набор точек для одной руки
            rect_flag = False  # флаг наждения всех точек руки в окне ввода
            hand_points = []  # координаты точек руки
            for id, lm in enumerate(handlms.landmark):  # id - номер точки на руке; lm - координаты в кадре (x, y, z)
                # print(id, lm)
                h, w, c = img.shape  # получить размер окна вывода изображения
                cx, cy = int(lm.x * w), int(lm.y * h)  # преобразуем координаты точки в понятные координаты по пикселям

                if not (40 <= cx <= 440 and 100 <= cy <= 500):
                    rect_flag = True  # если какая-то из точек руки не в рамке
                    text_timer = time()

                if id == 0: zeroX, zeroY = cx, cy  # координаты 0 точки

                hand_points.append([cx - zeroX, zeroY - cy])  # координаты точек в пикселях относительно 0 точки

                # составляем текущий вектор руки
                hand_vector.append(cx - zeroX)
                hand_vector.append(zeroY - cy)

                # print('{}: {}, {}'.format(id, cx, cy))

            # вывод координат точек и соединительных линий
            if not rect_flag:
                # for point in hand_points:
                #     cv2.putText(img, '{}, {}'.format(point[0], point[1]),
                #                 (point[0] - 25 + zeroX, zeroY - point[1] + 20),
                #                 cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 170), 1)
                # рисуем точки на руке и соединяем их
                mpDraw.draw_landmarks(img,  # выходное изображение
                                      handlms,  # точки на руке и их координаты
                                      mpHands.HAND_CONNECTIONS,  # определение связности точек на руке
                                      mp_drawing_styles.get_default_hand_landmarks_style(),
                                      mp_drawing_styles.get_default_hand_connections_style())

                # сравнение векторов
                res = find_match(hand_vector)   # - backspace + space
                sig = res
                if res == '0': continue
                elif res == '-': res = 'удалить'
                elif res == '+': res = 'пробел'

                if time() - text_timer > text_delay and sig == old_sig:
                    text_timer = time()
                    if res == 'удалить': text = text[:-1]
                    elif res == 'пробел': text += ' '
                    else: text += res

                old_sig = sig

                cv2.putText(img, res, (40, 600), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0), 2)
            else:
                cv2.putText(img, '___', (40, 600), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0), 2)
                text_timer = time()

    else:
        text_timer = time()

    # вычисление значения фпс
    cTime = time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, text, (500, 100), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 255, 0), 2)
    cv2.putText(img, 'fps: ' + str(int(fps)), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (139, 0, 0), 2)  # вставляем нарисованное в кадр + фпс
    cv2.putText(img, "Окно ввода текста:", (40, 90), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255))
    cv2.rectangle(img, (40, 100), (440, 500), (255, 255, 255), 4)
    cv2.imshow("Image", img)  # выводим кадр
    cv2.waitKey(1)
