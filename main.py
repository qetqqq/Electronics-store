import sys
import random
import mysql.connector
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QTableWidget, QTableWidgetItem, QMessageBox,
                               QComboBox, QDialog, QFormLayout, QDoubleSpinBox)
from PySide6.QtCore import Qt

# ==========================================
# НАСТРОЙКИ ПОДКЛЮЧЕНИЯ К БД
# ==========================================
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "1234",          # <--- ВПИШИ СВОЙ ПАРОЛЬ ОТ MYSQL
    "database": "tech_shop_db"
}

# Глобальная переменная для текущего пользователя
CURRENT_USER_ID = None

# ==========================================
# ОКНО РЕГИСТРАЦИИ
# ==========================================
class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация нового клиента")
        self.resize(300, 150)
        self.layout = QFormLayout(self)

        self.input_login = QLineEdit()
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.Password)

        self.layout.addRow("Придумайте логин:", self.input_login)
        self.layout.addRow("Придумайте пароль:", self.input_pass)

        self.btn_register = QPushButton("Зарегистрироваться")
        self.btn_register.clicked.connect(self.do_register)
        self.layout.addRow(self.btn_register)

    def do_register(self):
        login = self.input_login.text()
        password = self.input_pass.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            # Роль 2 - это Client
            cursor.execute("INSERT INTO users (login, password, role_id) VALUES (%s, %s, 2)", (login, password))
            conn.commit()
            QMessageBox.information(self, "Успех", "Вы успешно зарегистрированы! Теперь войдите.")
            self.accept() # Закрыть окно
        except mysql.connector.Error as err:
            if err.errno == 1062: # Ошибка дубликата
                QMessageBox.warning(self, "Ошибка", "Такой логин уже занят!")
            else:
                QMessageBox.critical(self, "Ошибка", f"Ошибка БД: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

# ==========================================
# ОКНО ДОБАВЛЕНИЯ ТОВАРА (Для админа)
# ==========================================
class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить товар")
        self.layout = QFormLayout(self)

        self.input_model = QLineEdit()
        self.input_price = QDoubleSpinBox()
        self.input_price.setMaximum(1000000)
        self.input_warranty = QLineEdit()

        self.combo_category = QComboBox()
        self.combo_manufacturer = QComboBox()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            for cat_id, cat_name in cursor.fetchall():
                self.combo_category.addItem(cat_name, cat_id)

            cursor.execute("SELECT id, name FROM manufacturers")
            for man_id, man_name in cursor.fetchall():
                self.combo_manufacturer.addItem(man_name, man_id)
            conn.close()
        except Exception:
            pass

        self.layout.addRow("Модель:", self.input_model)
        self.layout.addRow("Цена:", self.input_price)
        self.layout.addRow("Гарантия (мес):", self.input_warranty)
        self.layout.addRow("Категория:", self.combo_category)
        self.layout.addRow("Производитель:", self.combo_manufacturer)

        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self.accept)
        self.layout.addRow(self.btn_save)

# ==========================================
# ОКНО МОИХ ЗАКАЗОВ
# ==========================================
class OrdersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("История моих заказов")
        self.resize(700, 400)

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Номер заказа", "Товар", "Кол-во", "Дата"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.load_orders()

    def load_orders(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT o.id, p.model, oi.quantity, o.order_date
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE o.user_id = %s
                ORDER BY o.order_date DESC
            """
            cursor.execute(query, (CURRENT_USER_ID,))
            rows = cursor.fetchall()

            self.table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
            conn.close()
        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")

# ==========================================
# ОКНО АВТОРИЗАЦИИ
# ==========================================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.resize(300, 250)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Вход в систему")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)

        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Логин")

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Пароль")
        self.input_pass.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.check_login)
        self.btn_login.setStyleSheet("background-color: #a0d0ff; padding: 5px;")

        self.btn_open_register = QPushButton("Нет аккаунта? Зарегистрироваться")
        self.btn_open_register.setFlat(True)
        self.btn_open_register.setStyleSheet("color: blue; text-decoration: underline;")
        self.btn_open_register.clicked.connect(self.show_register)

        layout.addWidget(self.label)
        layout.addWidget(self.input_login)
        layout.addWidget(self.input_pass)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_open_register)
        self.setLayout(layout)

    def show_register(self):
        reg = RegisterWindow()
        reg.exec()

    def check_login(self):
        global CURRENT_USER_ID
        login = self.input_login.text()
        password = self.input_pass.text()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE login = %s AND password = %s", (login, password))
            user = cursor.fetchone()

            if user:
                CURRENT_USER_ID = user[0]
                self.main_window = MainWindow()
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Нет связи с БД:\n{e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

# ==========================================
# ГЛАВНОЕ ОКНО
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Магазин техники")
        self.resize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Панель управления
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию...")
        self.search_input.textChanged.connect(self.load_data)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории", None)
        self.load_filter_categories()
        self.filter_combo.currentIndexChanged.connect(self.load_data)

        self.btn_orders = QPushButton("Мои заказы")
        self.btn_orders.clicked.connect(self.show_orders_window)

        self.btn_style = QPushButton("Сменить цвет")
        self.btn_style.clicked.connect(self.change_color)

        top_layout.addWidget(QLabel("Поиск:"))
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(QLabel("Категория:"))
        top_layout.addWidget(self.filter_combo)
        top_layout.addWidget(self.btn_orders)
        top_layout.addWidget(self.btn_style)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6) # 5 колонок данных + 1 для кнопки
        self.table.setHorizontalHeaderLabels(["ID", "Модель", "Категория", "Бренд", "Цена", "Действие"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Кнопки админа
        bottom_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить товар (Админ)")
        self.btn_add.clicked.connect(self.add_product)

        self.btn_delete = QPushButton("Удалить товар (Админ)")
        self.btn_delete.setStyleSheet("background-color: #ffcccc;")
        self.btn_delete.clicked.connect(self.delete_product)

        bottom_layout.addWidget(self.btn_add)
        bottom_layout.addWidget(self.btn_delete)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(bottom_layout)

        self.load_data()

    def load_filter_categories(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            for cat_id, cat_name in cursor.fetchall():
                self.filter_combo.addItem(cat_name, cat_id)
            conn.close()
        except: pass

    def load_data(self):
        search_text = self.search_input.text()
        cat_id = self.filter_combo.currentData()

        query = """
            SELECT t.id, t.model, c.name, m.name, t.price 
            FROM products t
            JOIN categories c ON t.category_id = c.id
            JOIN manufacturers m ON t.manufacturer_id = m.id
            WHERE t.model LIKE %s
        """
        params = [f"%{search_text}%"]

        if cat_id:
            query += " AND t.category_id = %s"
            params.append(cat_id)

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            self.table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable) # Запрет на редактирование ячеек
                    self.table.setItem(row_idx, col_idx, item)

                # Кнопка "Купить"
                btn_buy = QPushButton("Купить")
                btn_buy.setStyleSheet("background-color: #ccffcc; font-weight: bold;")
                btn_buy.clicked.connect(lambda checked, p_id=row_data[0]: self.buy_product(p_id))
                self.table.setCellWidget(row_idx, 5, btn_buy)

            conn.close()
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

    def change_color(self):
        colors = ["#f0f8ff", "#fff0f5", "#f5fffa", "#fffff0", "#e6e6fa"]
        self.centralWidget().setStyleSheet(f"background-color: {random.choice(colors)};")

    def show_orders_window(self):
        self.orders_win = OrdersWindow()
        self.orders_win.show()

    def buy_product(self, product_id):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Создаем заказ
            cursor.execute("INSERT INTO orders (user_id, order_date, status) VALUES (%s, NOW(), 'Оплачен')", (CURRENT_USER_ID,))
            order_id = cursor.lastrowid

            # Добавляем товар в заказ
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, 1)", (order_id, product_id))

            conn.commit()
            QMessageBox.information(self, "Покупка", "Товар успешно куплен! Смотрите в 'Мои заказы'.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось купить: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    def add_product(self):
        dialog = AddProductDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO products (model, price, warranty_months, category_id, manufacturer_id) VALUES (%s, %s, %s, %s, %s)",
                    (
                        dialog.input_model.text(),
                        dialog.input_price.value(),
                        dialog.input_warranty.text(),
                        dialog.combo_category.currentData(),
                        dialog.combo_manufacturer.currentData()
                    )
                )
                conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Товар добавлен в каталог")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить: {e}")

    def delete_product(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Внимание", "Выберите товар для удаления")
            return

        product_id = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, "Удаление", f"Удалить товар ID {product_id}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Товар удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить (возможно, он уже куплен кем-то): {e}")

# ==========================================
# ЗАПУСК ПРОГРАММЫ
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())