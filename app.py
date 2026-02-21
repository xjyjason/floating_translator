import os
import sys
import threading
import ctypes
from ctypes import wintypes
from PySide6.QtCore import Qt, QPoint, Signal, QObject
from PySide6.QtGui import QColor, QPainter, QAction, QIcon, QRadialGradient
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QMessageBox, QSystemTrayIcon, QMenu, QStyle

from Baidu_Text_transAPI import translate_text


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


class GlobalHotkeyListener(QObject):
    hotkey_pressed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        user32 = ctypes.windll.user32
        MOD_ALT = 0x0001
        MOD_CONTROL = 0x0002
        WM_HOTKEY = 0x0312
        HOTKEY_ID = 1
        if not user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_ALT, ord('A')):
            return
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                self.hotkey_pressed.emit()
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        user32.UnregisterHotKey(None, HOTKEY_ID)


class FloatingBall(QWidget):
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(60, 60)
        self._drag_pos = QPoint()
        self._press_pos = QPoint()
        self._press_global = QPoint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        radius_rect = self.rect().adjusted(4, 4, -4, -4)
        shadow_rect = radius_rect.translated(2, 2)
        shadow_color = QColor(0, 0, 0, 90)
        painter.setBrush(shadow_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(shadow_rect)
        base_color = QColor('#1296db')
        gradient = QRadialGradient(radius_rect.center(), radius_rect.width() / 2, radius_rect.topLeft())
        gradient.setColorAt(0.0, base_color.lighter(180))
        gradient.setColorAt(0.4, base_color)
        gradient.setColorAt(1.0, base_color.darker(150))
        painter.setBrush(gradient)
        painter.drawEllipse(radius_rect)
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(int(radius_rect.height() * 0.35))
        painter.setFont(font)
        painter.drawText(radius_rect, Qt.AlignCenter, '译')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._press_pos = event.position().toPoint()
            self._press_global = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._press_global
            if delta.manhattanLength() < 5:
                self.clicked.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('悬浮翻译助手')
        self.resize(600, 400)
        self.ball = None
        self.lang_combo = QComboBox()
        self.input_edit = QTextEdit()
        self.output_edit = QTextEdit()
        self.translate_button = QPushButton('翻译')
        self.clipboard_button = QPushButton('剪贴板翻译')
        self.copy_result_button = QPushButton('复制结果')
        self.to_ball_button = QPushButton('退出程序')
        self.lang_map = {
            '自动检测→中文': ('auto', 'zh'),
            '自动检测→英文': ('auto', 'en'),
            '英文→中文': ('en', 'zh'),
            '中文→英文': ('zh', 'en'),
        }
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        self.lang_combo.addItems(self.lang_map.keys())
        self.lang_combo.setCurrentText('自动检测→中文')

        self.input_edit.setAcceptRichText(False)
        self.output_edit.setReadOnly(True)
        self.output_edit.setAcceptRichText(False)

        lang_layout = QHBoxLayout()
        lang_label = QLabel('语言方向')
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.translate_button)
        button_layout.addWidget(self.clipboard_button)
        button_layout.addWidget(self.copy_result_button)
        button_layout.addStretch()
        button_layout.addWidget(self.to_ball_button)

        layout = QVBoxLayout()
        layout.addLayout(lang_layout)
        layout.addWidget(QLabel('输入文本'))
        layout.addWidget(self.input_edit)
        layout.addWidget(QLabel('翻译结果'))
        layout.addWidget(self.output_edit)
        layout.addLayout(button_layout)

        central.setLayout(layout)

        self.translate_button.clicked.connect(self.translate_current_text)
        self.clipboard_button.clicked.connect(self.translate_from_clipboard)
        self.copy_result_button.clicked.connect(self.copy_result_to_clipboard)
        self.to_ball_button.clicked.connect(self.exit_app)

    def set_ball(self, ball):
        self.ball = ball

    def current_langs(self):
        key = self.lang_combo.currentText()
        return self.lang_map.get(key, ('auto', 'zh'))

    def _clean_text(self, text):
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = text.strip()
        lines = [line.strip() for line in text.split('\n')]
        cleaned_lines = []
        last_blank = False
        for line in lines:
            if not line:
                if not last_blank:
                    cleaned_lines.append('')
                last_blank = True
            else:
                cleaned_lines.append(line)
                last_blank = False
        return '\n'.join(cleaned_lines)

    def copy_result_to_clipboard(self):
        text = self.output_edit.toPlainText()
        if not text:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def translate_current_text(self):
        text = self._clean_text(self.input_edit.toPlainText())
        if not text:
            return
        source_lang, target_lang = self.current_langs()
        try:
            result = translate_text(text, source_lang, target_lang)
        except Exception as exc:
            QMessageBox.critical(self, '翻译失败', str(exc))
            return
        self.output_edit.setPlainText(result)

    def translate_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = self._clean_text(clipboard.text())
        if not text:
            return
        self.input_edit.setPlainText(text)
        self.translate_current_text()

    def minimize_to_ball(self):
        self.hide()
        if self.ball is not None:
            self.ball.show()
            self.ball.raise_()
            self.ball.activateWindow()

    def exit_app(self):
        app = QApplication.instance()
        if app is not None:
            app.setProperty('quitting', True)
            app.quit()

    def closeEvent(self, event):
        app = QApplication.instance()
        if app is not None and app.property('quitting'):
            super().closeEvent(event)
            return
        self.minimize_to_ball()
        event.ignore()


def create_tray(app, main_window, ball, icon):
    if icon.isNull():
        icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
    tray = QSystemTrayIcon(icon, app)
    menu = QMenu()
    show_main_action = QAction('显示主窗口', menu)
    show_ball_action = QAction('显示悬浮球', menu)
    exit_action = QAction('退出', menu)

    menu.addAction(show_main_action)
    menu.addAction(show_ball_action)
    menu.addSeparator()
    menu.addAction(exit_action)

    tray.setContextMenu(menu)

    def show_main():
        ball.hide()
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()

    def show_ball():
        main_window.hide()
        ball.show()
        ball.raise_()
        ball.activateWindow()

    def exit_app():
        tray.hide()
        app.setProperty('quitting', True)
        app.quit()

    show_main_action.triggered.connect(show_main)
    show_ball_action.triggered.connect(show_ball)
    exit_action.triggered.connect(exit_app)

    tray.show()
    return tray


def main():
    app = QApplication(sys.argv)
    app.setProperty('quitting', False)
    icon = QIcon(resource_path('logo/translater.svg'))
    main_window = MainWindow()
    screen = app.primaryScreen()
    main_window.setWindowIcon(icon)
    ball = FloatingBall()
    main_window.set_ball(ball)

    if screen is not None:
        rect = screen.availableGeometry()

        ball_x = rect.x() + rect.width() - ball.width() - 20
        ball_y = rect.y() + rect.height() - ball.height() - 20
        ball.move(ball_x, ball_y)

        main_x = rect.x() + rect.width() - main_window.width() - 40
        main_y = rect.y() + rect.height() - main_window.height() - 120
        if main_y < rect.y():
            main_y = rect.y()
        main_window.move(main_x, main_y)

    def on_ball_clicked():
        ball.hide()
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()

    ball.clicked.connect(on_ball_clicked)

    def toggle_main():
        if main_window.isVisible():
            main_window.minimize_to_ball()
        else:
            ball.hide()
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()

    shortcut_action = QAction(main_window)
    shortcut_action.setShortcut('Ctrl+Alt+A')
    shortcut_action.setShortcutContext(Qt.ApplicationShortcut)
    shortcut_action.triggered.connect(toggle_main)
    main_window.addAction(shortcut_action)

    hotkey_listener = GlobalHotkeyListener(app)
    hotkey_listener.hotkey_pressed.connect(toggle_main)

    create_tray(app, main_window, ball, icon)

    ball.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
