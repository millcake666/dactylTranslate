import cv2
import mediapipe as mp
from time import time, sleep


file_flag = True
time_to_print = 3
time_to_write = 1
cap = cv2.VideoCapture(1)  # захват изображения
mpHands = mp.solutions.hands  # класс для построения связи между опорными точками
hands = mpHands.Hands()  # класс для нахождения опорных точек руки
mpDraw = mp.solutions.drawing_utils  # используется для отображения результатов
mp_drawing_styles = mp.solutions.drawing_styles
zeroX, zeroY = 0, 0  # храниение координат 0 точки (опорной)
text_vector = ''

sleep(0.1)
sign = input('Для какой буквы запишем вектор?\n--> ')

switch_time_print = time()
switch_time_write = time()


while True:
    _, img = cap.read()  # получаем кадр
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # конвертируем из BGR в RGB
    results = hands.process(imgRGB)  # находим опорные точки
    res = results.multi_hand_landmarks  # список рук, точек и координат соответственно

    if res:

        if len(res) != 1:
            cv2.putText(img, "В кадре должна быть только одна рука!", (100, 600),
                        cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 255), 2)
            cv2.imshow("Image", img)  # выводим кадр
            cv2.waitKey(1)
            switch_time_print = time()
            continue

        hand_vector = []  # вектор руки
        rect_flag = False
        for id, lm in enumerate(res[0].landmark):  # id - номер точки на руке; lm - координаты в кадре (x, y, z)
            h, w, c = img.shape  # получить размер окна вывода изображения
            cx, cy = int(lm.x * w), int(lm.y * h)  # преобразуем координаты точки в понятные координаты по пикселям
            if id == 0: zeroX, zeroY = cx, cy  # координаты 0 точки

            # если какая-то из точек руки не в рамке
            if not (40 <= cx <= 440 and 100 <= cy <= 500): rect_flag = True

            if not rect_flag:
                hand_vector.append(cx - zeroX)
                hand_vector.append(zeroY - cy)

        if not rect_flag:
            rect_flag = False
            mpDraw.draw_landmarks(img,  # выходное изображение
                                  res[0],  # точки на руке и их координаты
                                  mpHands.HAND_CONNECTIONS,  # определение связности точек на руке
                                  mp_drawing_styles.get_default_hand_landmarks_style(),
                                  mp_drawing_styles.get_default_hand_connections_style())

        if time() - switch_time_print > time_to_print and len(hand_vector) == 42:
            file_hand_vectors = open(f'hand_vectors.txt', 'r+')
            text_vector = f'{sign}:'
            for s in hand_vector:
                text_vector += f'{s},'
            text_vector = text_vector[:-1] + ';'
            print(text_vector)
            ans = int(input('Записать? (1/0)\n--> '))
            if ans:
                print(f'[INFO] Write vector to file with "{sign}" sign...')

                if len(file_hand_vectors.readlines()) > 0:
                    file_hand_vectors.writelines('\n' + text_vector)
                else:
                    file_hand_vectors.writelines(text_vector)
                file_hand_vectors.close()
                print(f'[INFO] Write vector was complete!')

            else:
                file_hand_vectors.close()
                print(f'[INFO] Save was rejected')

            sign = input('Для какой еще буквы запишем вектор?\n--> ')

    if time() - switch_time_print > time_to_print:
        switch_time_print = time()
    cv2.putText(img, str(round(3 - (time() - switch_time_print))), (600, 400),
                cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255))
    cv2.putText(img, "Окно ввода текста:", (40, 90), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255))
    cv2.rectangle(img, (40, 100), (440, 500), (255, 255, 255), 4)
    cv2.imshow("Image", img)  # выводим кадр
    cv2.waitKey(1)
