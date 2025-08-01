from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit


class LoginWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()

        login_widget = QWidget()


        username_line_edit = QLineEdit()
        password_line_edit = QLineEdit()
        confirm_btn = QPushButton("Login")

        login_form_layout = QVBoxLayout(login_widget)
        login_form_layout.addWidget(username_line_edit)
        login_form_layout.addWidget(password_line_edit)
        login_form_layout.addWidget(confirm_btn)

        label = QLabel()
        image = QPixmap("../../../../resources/screens/login/login_banner.png")
        label.setPixmap(image)

        main_layout.addWidget(label)
        main_layout.addWidget(login_widget)
        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication([])
    window = LoginWidget()
    window.show()
    app.exec()
