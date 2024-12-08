import cv2
from pyzbar.pyzbar import decode
import numpy as np
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime  # Импортируем модуль для работы с датой и временем

# Функция для создания и подключения к базе данных
def create_db():
    conn = sqlite3.connect('qr_codes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  -- Добавляем поле для времени
        )
    ''')
    conn.commit()
    return conn

# Функция для добавления QR-кода в базу данных
def add_to_db(conn, qr_data):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO qr_codes (data) VALUES (?)', (qr_data,))
    conn.commit()

# Функция для удаления QR-кода из базы данных
def delete_from_db(conn, qr_data):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM qr_codes WHERE data = ?', (qr_data,))
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
    cursor.execute('SELECT data, timestamp FROM qr_codes')  # Изменяем запрос для получения времени
    rows = cursor.fetchall()
    
    if rows:
        for row in rows:
            text_area.insert(tk.END, f"Данные: {row[0]}, Время добавления: {row[1]}\n")  # Отображаем данные и время
    else:
        text_area.insert(tk.END, "Нет данных в базе.")

    button_close = tk.Button(window, text="Закрыть", command=window.destroy)
    button_close.pack(pady=5)

    window.mainloop()

# Функция для удаления QR-кода
def delete_qr_code():
    delete_window = tk.Tk()
    delete_window.title("Удаление QR-кода")

    label = tk.Label(delete_window, text="Введите данные QR-кода для удаления:")
    label.pack(pady=10)

    qr_data_entry = tk.Entry(delete_window, width=40)
    qr_data_entry.pack(pady=5)

    def confirm_delete():
        qr_data = qr_data_entry.get()
        delete_from_db(conn, qr_data)
        messagebox.showinfo("Успех", "QR-код успешно удален из базы данных!")
        delete_window.destroy()

    button_delete = tk.Button(delete_window, text="Удалить", command=confirm_delete)
    button_delete.pack(pady=5)

    button_close = tk.Button(delete_window, text="Закрыть", command=delete_window.destroy)
    button_close.pack(pady=5)

    delete_window.mainloop()

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

            show_qr_data(qr_data)  # Показываем данные QR-кода

        cv2.imshow('QR Code Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    global conn
    conn = create_db()  # Создаем и подключаемся к базе данных

    root = tk.Tk()
    root.title("QR Code Scanner")

    start_button = tk.Button(root, text="Начать сканирование", command=start_scanning)
    start_button.pack(pady=20)

    show_button = tk.Button(root, text="Показать все QR-коды", command=show_all_data)
    show_button.pack(pady=20)

    delete_button = tk.Button(root, text="Удалить QR-код", command=delete_qr_code)
    delete_button.pack(pady=20)

    root.mainloop()  # Запускаем главное окно

if __name__ == "__main__":
    main()