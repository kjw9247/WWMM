import sys
import os
import glob
import shutil
import subprocess
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox, QScrollArea, QFrame, QGridLayout,
    QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtGui import QPixmap, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFontDatabase, QFont

class WWMM(QWidget):
    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WWMM - Wuthering Waves Mod Manager")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "./WWMM_icon.ico")))
        self.resize(1200, 700)

        self.wwmm_mods_path = os.path.abspath(os.path.join(os.getcwd(), "Mods"))
        self.wwmi_mods_path = None
        self.settings_file = os.path.join(os.getcwd(), "settings.json")

        self.current_character = None
        self.character_order = []

        self.init_ui()
        self.load_settings()
        self.load_characters()

    def init_ui(self):
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)

        main_layout = QVBoxLayout()
        title_bar = QHBoxLayout()
        title_bar_widget = QWidget()
        title_bar_widget.setFixedHeight(53)
        title_bar_widget.setLayout(title_bar)
        title_bar_widget.setStyleSheet("background-color: #2e2e2e;")

        title = QLabel("WWMM - Wuthering Waves Mod Manager")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 20px; padding-left: 8px;")
        title.setContentsMargins(0, -2, 0, 0)
        title.setFixedHeight(36)
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        minimize_button = QPushButton("―")
        minimize_button.setFixedSize(36, 36)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                font-size: 20px;
                border: none;
                padding: -1px;
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)

        maximize_button = QPushButton("□")
        maximize_button.setFixedSize(36, 36)
        maximize_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                font-size: 20px;
                border: none;
                padding: -1px;
            }
        """)
        maximize_button.clicked.connect(self.toggle_maximize_restore)

        close_button = QPushButton("✕")
        close_button.setFixedSize(36, 36)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                font-size: 20px;
                border: none;
                padding: -1px;
            }
        """)
        close_button.clicked.connect(self.close)

        title_bar.addWidget(title, alignment=Qt.AlignVCenter)
        title_bar.addStretch()
        title_bar.addWidget(minimize_button, alignment=Qt.AlignVCenter)
        title_bar.addWidget(maximize_button, alignment=Qt.AlignVCenter)
        title_bar.addWidget(close_button, alignment=Qt.AlignVCenter)

        top_bar = QHBoxLayout()
        content_layout = QHBoxLayout()

        self.path_label = QLabel("WWMI Path: (미설정)")
        self.path_label.setStyleSheet("color: white;")
        self.set_path_button = QPushButton("WWMI Route Setting")
        self.set_path_button.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #666;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5c5c5c;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
        """)

        top_bar.addWidget(self.path_label)
        top_bar.addWidget(self.set_path_button)
        self.set_path_button.clicked.connect(self.set_wwmi_path)

        # 왼쪽: 속성별 캐릭터 QTreeWidget
        self.character_list = QTreeWidget()
        self.character_list.setHeaderHidden(True)
        self.character_list.setStyleSheet("""
            QTreeWidget {
                background-color: #2e2e2e;
                color: white;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: #444;
                color: white;
            }
        """)
        self.character_list.itemClicked.connect(self.on_character_selected)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.mod_cards_container = QWidget()
        self.mod_cards_layout = QGridLayout()
        self.mod_cards_container.setLayout(self.mod_cards_layout)
        self.scroll_area.setWidget(self.mod_cards_container)
        self.scroll_area.setStyleSheet("background-color: #1e1e1e;")

        content_layout.addWidget(self.character_list, 2)
        content_layout.addWidget(self.scroll_area, 5)

        main_layout.addWidget(title_bar_widget)
        main_layout.addLayout(top_bar)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def set_wwmi_path(self):
        path = QFileDialog.getExistingDirectory(self, "WWMI의 Mods 폴더 선택")
        if path:
            self.wwmi_mods_path = os.path.abspath(path)
            self.path_label.setText(f"WWMI Path: {self.wwmi_mods_path}")
            self.save_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.wwmi_mods_path = data.get("wwmi_mods_path")
                    self.character_order = data.get("character_order", [])
                    if self.wwmi_mods_path:
                        self.path_label.setText(f"WWMI Path: {self.wwmi_mods_path}")
            except Exception as e:
                print(f"[설정 로드 실패] {e}")

    def save_settings(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump({
                    "wwmi_mods_path": self.wwmi_mods_path,
                    "character_order": self.character_order
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[설정 저장 실패] {e}")

    def load_characters(self):
        self.character_list.clear()
        if not os.path.isdir(self.wwmm_mods_path):
            QMessageBox.warning(self, "오류", f"WWMM의 Mods 폴더가 없습니다:\n{self.wwmm_mods_path}")
            return

        # 속성별 카테고리와 캐릭터
        categories = {
            "응결": ["설지", "산화", "능양", "절지", "유호", "카를로타"],
            "용융": ["치샤", "모르테피", "앙코", "장리", "브렌트", "루파"],
            "전도": ["연무", "카카루", "음림", "상리요", "루미"],
            "기류": ["양양", "알토", "감심", "기염", "샤콘", "카르티시아"],
            "회절": ["벨리나", "금희", "파수인", "페비", "젠니"],
            "인멸": ["단근", "도기", "카멜리아", "로코코", "칸타렐라"]
        }
        wanderer = ["방랑자"]

        # 실제 Mods 폴더에 존재하는 캐릭터만 표시
        all_char_dirs = [
            d for d in os.listdir(self.wwmm_mods_path)
            if os.path.isdir(os.path.join(self.wwmm_mods_path, d))
        ]

        # 방랑자(단독 노드)
        for char in wanderer:
            if char in all_char_dirs:
                QTreeWidgetItem(self.character_list, [char])

        # 카테고리별 노드
        for category, char_list in categories.items():
            cat_item = QTreeWidgetItem([category])
            has_child = False
            for char in char_list:
                if char in all_char_dirs:
                    QTreeWidgetItem(cat_item, [char])
                    has_child = True
            if has_child:
                self.character_list.addTopLevelItem(cat_item)

    def clear_mod_cards(self):
        while self.mod_cards_layout.count():
            item = self.mod_cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def on_character_selected(self, item, _=None):
        # 카테고리(부모)는 클릭시 동작 X
        if item.childCount() > 0:
            return
        char_name = item.text(0)
        self.current_character = char_name
        char_mod_path = os.path.join(self.wwmm_mods_path, char_name)
        applied_mod = self.get_applied_mod_name(char_name)

        self.clear_mod_cards()

        if not os.path.isdir(char_mod_path):
            return

        mod_folders = [
            d for d in os.listdir(char_mod_path)
            if os.path.isdir(os.path.join(char_mod_path, d))
        ]
        if not mod_folders:
            self.add_mod_card("모드 없음", None, False, False, 0, 0)
            return

        for idx, mod_name in enumerate(sorted(mod_folders)):
            mod_path = os.path.join(char_mod_path, mod_name)
            preview_path = self.get_preview_image_path(mod_path)
            is_applied = (mod_name == applied_mod)
            row, col = divmod(idx, 2)
            self.add_mod_card(mod_name, preview_path, is_applied, True, row, col)

    def add_mod_card(self, mod_name, image_path, is_applied, can_apply, row, col):
        card = QFrame()
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card.setFrameShape(QFrame.Box)
        card.setLineWidth(1)
        card.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
                border: 1px solid #444;
                border-radius: 10px;
                padding: 10px;
                color: white;
            }
        """)

        title = QLabel(f"모드 이름: {mod_name}" + (" ✅ 적용됨" if is_applied else ""))
        title.setAlignment(Qt.AlignCenter)

        preview = QLabel()
        preview.setAlignment(Qt.AlignCenter)

        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                preview.setText("이미지 로딩 실패")
                preview.setFixedSize(300, 200)
            else:
                preview.setPixmap(pixmap.scaled(QSize(300, 200), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            preview.setText("미리보기 없음")
            preview.setFixedSize(300, 200)

        if can_apply:
            button = QPushButton("해제하기" if is_applied else "적용하기")
            button.clicked.connect(lambda _, m=mod_name, a=is_applied: self.toggle_mod(m, a))
            card_layout.addWidget(button)

        card_layout.addWidget(title)
        card_layout.addWidget(preview)
        self.mod_cards_layout.addWidget(card, row, col)

    def toggle_mod(self, mod_name, is_applied):
        if not self.current_character or not self.wwmi_mods_path:
            QMessageBox.warning(self, "오류", "WWMI 경로가 설정되어 있지 않습니다.")
            return

        char_name = self.current_character
        target_path = os.path.join(self.wwmi_mods_path, char_name)

        if is_applied:
            try:
                if os.path.exists(target_path):
                    if os.path.islink(target_path):
                        os.unlink(target_path)
                    else:
                        shutil.rmtree(target_path)
            except Exception as e:
                QMessageBox.warning(self, "오류", f"해제 실패:\n{e}")
        else:
            selected_mod_path = os.path.join(self.wwmm_mods_path, char_name, mod_name)
            self.create_symlink_windows_compatible(selected_mod_path, target_path)

        # 캐릭터 노드 다시 새로고침
        for i in range(self.character_list.topLevelItemCount()):
            item = self.character_list.topLevelItem(i)
            if item.childCount() == 0 and item.text(0) == char_name:
                self.on_character_selected(item)
                return
            for j in range(item.childCount()):
                child = item.child(j)
                if child.text(0) == char_name:
                    self.on_character_selected(child)
                    return

    def create_symlink_windows_compatible(self, src, dst):
        src = os.path.abspath(src)
        dst = os.path.abspath(dst)

        if not os.path.exists(src):
            QMessageBox.warning(self, "오류", f"원본 모드 경로가 존재하지 않습니다:\n{src}")
            return

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        if os.path.exists(dst):
            try:
                if os.path.islink(dst):
                    os.unlink(dst)
                else:
                    shutil.rmtree(dst)
            except Exception as e:
                QMessageBox.warning(self, "오류", f"기존 링크 제거 실패:\n{e}")
                return

        try:
            cmd = f'mklink /D "{dst}" "{src}"'
            subprocess.call(f'cmd /c {cmd}', shell=True)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"mklink 명령 실패:\n{e}")

    def get_applied_mod_name(self, character_name):
        if not self.wwmi_mods_path:
            return None
        target_path = os.path.join(self.wwmi_mods_path, character_name)
        if os.path.islink(target_path):
            linked_path = os.readlink(target_path)
            return os.path.basename(os.path.normpath(linked_path))
        return None

    def get_preview_image_path(self, mod_path):
        candidates = glob.glob(os.path.join(mod_path, "Preview.*"))
        return os.path.abspath(candidates[0]) if candidates else None

if __name__ == "__main__":
    import ctypes
    myappid = 'wwmm.modmanager.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)

    font_path = os.path.join(os.getcwd(), "./AstaSans-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(family, 13))
    else:
        print("AstaSans 폰트 로드 실패")
    app.setStyle("Fusion")

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)

    window = WWMM()
    window.show()
    sys.exit(app.exec_())
