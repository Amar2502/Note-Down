import sys

from PyQt6.QtCore import Qt, QTimer, QPoint, QVariantAnimation
from PyQt6.QtGui import QColor, QPainter, QPen, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QToolTip, QDialog, QLineEdit
)

import core

# ------------------ TOAST ------------------

class Toast(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWordWrap(True)
        self._apply_style("info")
        self.hide()

    def _apply_style(self, level):
        styles = {
            "info": ("rgba(20, 20, 20, 230)", "rgba(255, 255, 255, 40)"),
            "success": ("rgba(16, 60, 30, 235)", "rgba(80, 220, 130, 120)"),
            "error": ("rgba(70, 22, 22, 235)", "rgba(255, 110, 110, 120)")
        }
        bg, border = styles.get(level, styles["info"])
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: white;
                border: 1px solid {border};
                border-radius: 10px;
                padding: 6px 10px;
                font-size: 10px;
                font-weight: 500;
            }}
        """)

    def show_message(self, text, level="info", duration=2200):
        self._apply_style(level)
        self.setText(text)
        self.setMaximumWidth(max(180, self.parent().width() - 16))
        self.adjustSize()
        self.move(
            (self.parent().width() - self.width()) // 2,
            self.parent().height() - self.height() - 12
        )
        self.show()
        QTimer.singleShot(duration, self.hide)


# ------------------ SESSION DIALOG ------------------

class SessionNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start Session")
        self.setModal(True)
        self.setFixedWidth(320)

        self.setStyleSheet("""
            QDialog {
                background: #101524;
                color: #e8ecff;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 12px;
            }
            QLabel {
                color: #d9e0ff;
                font-size: 11px;
            }
            QLineEdit {
                background: rgba(255, 255, 255, 18);
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 8px;
                padding: 7px 10px;
                color: white;
                selection-background-color: rgba(90, 150, 255, 120);
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 7px 12px;
                font-size: 10px;
                font-weight: 600;
            }
            QPushButton#cancelBtn {
                background: rgba(255, 255, 255, 20);
                color: #d6dcf5;
            }
            QPushButton#okBtn {
                background: rgba(72, 140, 255, 200);
                color: white;
            }
            QPushButton:hover#cancelBtn {
                background: rgba(255, 255, 255, 30);
            }
            QPushButton:hover#okBtn {
                background: rgba(85, 152, 255, 235);
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("Enter session name")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. meeting-notes")
        self.name_input.returnPressed.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        ok_btn = QPushButton("Start")
        cancel_btn.setObjectName("cancelBtn")
        ok_btn.setObjectName("okBtn")
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)

        root.addWidget(title)
        root.addWidget(self.name_input)
        root.addLayout(buttons)

    def get_name(self):
        return self.name_input.text().strip()


# ------------------ BUTTON ------------------

class CircleButton(QPushButton):
    def __init__(self, icon_path, tooltip):
        super().__init__()

        self.base_alpha = 0.06

        self.setFixedSize(44, 44)
        self.setToolTip(tooltip)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(self.size() * 0.5)

        self.update_style(self.base_alpha)

    def update_style(self, alpha):
        self.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,{alpha});
                border-radius: 22px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.15);
            }}
        """)

    # 🔥 Smooth pulse WITHOUT pyqtProperty
    def pulse(self):
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(600)
        self.anim.setStartValue(0.06)
        self.anim.setKeyValueAt(0.5, 0.25)
        self.anim.setEndValue(0.06)

        self.anim.valueChanged.connect(self.update_style)
        self.anim.start()
# ------------------ MAIN UI ------------------

class FloatingPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Slightly taller panel for logo + toast breathing space
        self.setFixedSize(74, 320)

        self.drag_pos = QPoint()

        self.session_active = False
        self.audio_active = False

        # Layout
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.brand_label = QLabel("NOTEDOWN")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand_label.setStyleSheet("""
            QLabel {
                color: rgba(220, 230, 255, 190);
                font-size: 8px;
                font-weight: 700;
                letter-spacing: 1.1px;
                padding-bottom: 2px;
            }
            QLabel:hover { color: rgba(200, 220, 255, 255); }
        """)

        self.session_btn = CircleButton("ui_utils/start.svg", "Start / End Session")
        self.text_btn = CircleButton("ui_utils/text.svg", "Capture Text")
        self.image_btn = CircleButton("ui_utils/image.svg", "Capture Image")
        self.audio_btn = CircleButton("ui_utils/audio.svg", "Record Audio")

        layout.addWidget(self.brand_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(6)
        layout.addWidget(self.session_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.audio_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        # Toast
        self.toast = Toast(self)

        # Connect
        self.session_btn.clicked.connect(self.toggle_session)
        self.text_btn.clicked.connect(self.get_text)
        self.image_btn.clicked.connect(self.get_image)
        self.audio_btn.clicked.connect(self.toggle_audio)

    def _show_action_error(self,  error):
        error_text = str(error).strip() or "Unknown error"
        self.toast.show_message(f"{error_text}", "error", 3200)

    def _ensure_session_active(self):
        if self.session_active:
            return True
        self.toast.show_message(f"start session first", "error", 2500)
        return False

    # ------------------ GLASS PANEL ------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(10, 15, 30, 200))
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))

        painter.drawRoundedRect(self.rect(), 18, 18)

    # ------------------ ACTIONS ------------------

    def toggle_session(self):
        try:
            if not self.session_active:
                dialog = SessionNameDialog(self)
                dialog.name_input.setFocus()
                ok = dialog.exec() == QDialog.DialogCode.Accepted
                name = dialog.get_name()
                if not ok or not name:
                    return

                core.start_session(name)
                self.session_active = True
                self.session_btn.setIcon(QIcon("ui_utils/stop.svg"))
                self.toast.show_message("Session started", "success")

            else:
                core.end_session()
                self.session_active = False
                self.session_btn.setIcon(QIcon("ui_utils/start.svg"))
                self.audio_active = False
                self.audio_btn.setIcon(QIcon("ui_utils/audio.svg"))
                self.toast.show_message("Session ended", "info")

        except Exception as e:
            self._show_action_error(e)

    def get_text(self):
        if not self._ensure_session_active():
            return
        try:
            core.handle_text()
            self.toast.show_message("Text saved", "success")
            self.text_btn.pulse()
        except Exception as e:
            self._show_action_error( e)

    def get_image(self):
        if not self._ensure_session_active():
            return
        try:
            core.handle_image()
            self.toast.show_message("Image saved", "success")
            self.image_btn.pulse()
        except Exception as e:
            self._show_action_error( e)

    def toggle_audio(self):
        if not self._ensure_session_active():
            return
        try:
            core.handle_audio()
            self.audio_active = not self.audio_active

            if self.audio_active:
                self.audio_btn.setIcon(QIcon("ui_utils/music.svg"))
                self.toast.show_message("Recording...", "info")
            else:
                self.audio_btn.setIcon(QIcon("ui_utils/audio.svg"))
                self.toast.show_message("Audio saved", "success")
                self.audio_btn.pulse()
        except Exception as e:
            self._show_action_error( e)

    # ------------------ DRAG ------------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_pos = event.globalPosition().toPoint()


# ------------------ MAIN ------------------

def main():
    app = QApplication(sys.argv)
    QToolTip.setFont(QFont("Segoe UI", 9))  # 🔥 better tooltip font

    ui = FloatingPanel()
    ui.move(200, 200)
    ui.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()