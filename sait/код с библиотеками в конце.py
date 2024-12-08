import cv2
from pyzbar.pyzbar import decode
import numpy as np
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Функция для создания и подключения к базе данных
def create_db():
    conn = sqlite3.connect('qr_codes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

# Функция для добавления QR-кода в базу данных
def add_to_db(conn, qr_data):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO qr_codes (data) VALUES (?)', (qr_data,))
    conn.commit()

# Функция для отображения всех данных из базы данных
def show_all_data():
    window = tk.Tk()
    window.title("Список всех QR-кодов")

    # Создаем текстовое поле с прокруткой для отображения данных
    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=50, height=20)
    text_area.pack(pady=10)

    # Извлекаем данные из базы данных и отображаем их
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM qr_codes')
    rows = cursor.fetchall()
    
    if rows:
        for row in rows:
            text_area.insert(tk.END, f"{row[0]}\n")
    else:
        text_area.insert(tk.END, "Нет данных в базе.")

    button_close = tk.Button(window, text="Закрыть", command=window.destroy)
    button_close.pack(pady=5)

    window.mainloop()

# Функция для отображения окна с данными QR-кода
def show_qr_data(qr_data):
    window = tk.Tk()
    window.title("QR Code Data")
    
    label = tk.Label(window, text=f"Данные QR-кода:\n{qr_data}")
    label.pack(pady=10)

    button_add = tk.Button(window, text="Добавить в базу данных", command=lambda: add_and_close(window, qr_data))
    button_add.pack(pady=5)

    button_show_all = tk.Button(window, text="Показать все данные", command=lambda: [window.destroy(), show_all_data()])
    button_show_all.pack(pady=5)

    window.mainloop()

def add_and_close(window, qr_data):
    add_to_db(conn, qr_data)
    messagebox.showinfo("Успех", "Данные успешно добавлены в базу данных!")
    window.destroy()

def start_scanning():
    global cap
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Не удалось открыть камеру.")
        return

    while True:
        # Читаем кадр из камеры
        ret, frame = cap.read()
        if not ret:
            print("Не удалось получить кадр.")
            break

        # Декодируем QR-коды на текущем кадре
        decoded_objects = decode(frame)

        for obj in decoded_objects:
            # Извлекаем данные из QR-кода
            qr_data = obj.data.decode('utf-8')
            qr_type = obj.type

            # Рисуем прямоугольник вокруг QR-кода
            points = obj.polygon
            if len(points) == 4:  # Проверяем, что это четырехугольник
                cv2.polylines(frame, [np.array(points)], isClosed=True, color=(0, 255, 0), thickness=2)

            # Выводим данные QR-кода на экран
            cv2.putText(frame, f'{qr_data} ({qr_type})', (obj.rect.left, obj.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Показать окно с данными QR-кода
            show_qr_data(qr_data)

        # Отображаем кадр с QR-кодами
        cv2.imshow('QR Code Scanner', frame)

        # Выход из цикла по нажатию клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождаем ресурсы
    cap.release()
    cv2.destroyAllWindows()

def create_menu(root):
    menu = tk.Menu(root)
    
    # Создаем меню "Файл"
    file_menu = tk.Menu(menu, tearoff=0)
    file_menu.add_command(label="Показать все QR-коды", command=show_all_data)
    
    menu.add_cascade(label="Файл", menu=file_menu)
    # Создаем меню "Сканировать"
    scan_menu = tk.Menu(menu, tearoff=0)
    scan_menu.add_command(label="Начать сканирование", command=start_scanning)
    
    menu.add_cascade(label="Сканировать", menu=scan_menu)

    root.config(menu=menu)

def main():
    global conn
    conn = create_db()  # Создаем и подключаемся к базе данных

    root = tk.Tk()
    root.title("QR Code Scanner")

    create_menu(root)  # Создаем меню

    root.mainloop()  # Запускаем главное окно

if __name__ == "__main__":  # Исправлено условие
    main()



    # чтобы нормально всё работало нужны библиотеки:
    #     1)   pip install opencv-python
    #     2)   pip install pyzbar
   