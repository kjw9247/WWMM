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
from PyQt5.QtGui import QFontDatabase, QFont, QBrush, QColor

class WWMM(QWidget):
    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

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
        self.old_pos = None

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
        self.title_bar_widget = title_bar_widget   # 멤버 변수화
        self.title_bar_widget.mousePressEvent = self.title_bar_mousePressEvent
        self.title_bar_widget.mouseMoveEvent = self.title_bar_mouseMoveEvent

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
        self.character_list.setIconSize(QSize(45, 45))
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

        # 버튼 생성 및 배치
        self.launch_xxmi_button = QPushButton("Run XXMI Launcher")
        self.launch_xxmi_button.setStyleSheet("""
            QPushButton {
                background-color: #4a69bd;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e3799;
            }
        """)
        self.launch_xxmi_button.clicked.connect(self.launch_xxmi_launcher)
        top_bar.addWidget(self.launch_xxmi_button)

        self.mod_cards_layout = QGridLayout()
        self.mod_cards_vbox = QVBoxLayout()
        self.add_mod_button = QPushButton("＋ 모드 추가")
        self.add_mod_button.setFixedHeight(34)
        self.add_mod_button.setStyleSheet("""
            QPushButton {
                background-color: #333c;
                color: #fff;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin-bottom: 8px;
            }
            QPushButton:hover {
                background-color: #47535f;
            }
        """)
        self.add_mod_button.clicked.connect(lambda: self.add_mod_folder(self.current_character))
        self.mod_cards_vbox.addWidget(self.add_mod_button)
        self.mod_cards_vbox.addLayout(self.mod_cards_layout)
        self.mod_cards_container.setLayout(self.mod_cards_vbox)

    def title_bar_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def title_bar_mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.old_pos is not None:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()        

        # 실행 함수 위치
    def launch_xxmi_launcher(self):
        if not hasattr(self, "xxmi_launcher_path") or not self.xxmi_launcher_path or not os.path.exists(self.xxmi_launcher_path):
            QMessageBox.warning(self, "경로 오류", "XXMI Launcher 실행 파일 경로를 먼저 설정해주세요.")
            self.set_xxmi_launcher_path()
            # 경로를 설정했다면 곧바로 실행
            if hasattr(self, "xxmi_launcher_path") and self.xxmi_launcher_path and os.path.exists(self.xxmi_launcher_path):
                try:
                    subprocess.Popen([self.xxmi_launcher_path], shell=True)
                except Exception as e:
                    QMessageBox.critical(self, "실행 실패", f"XXMI Launcher 실행 중 오류:\n{e}")
            return
        try:
            subprocess.Popen([self.xxmi_launcher_path], shell=True)
        except Exception as e:
            QMessageBox.critical(self, "실행 실패", f"XXMI Launcher 실행 중 오류:\n{e}")

    def set_xxmi_launcher_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "XXMI Launcher 실행파일 선택", "", "실행 파일 (*.exe)")
        if path:
            self.xxmi_launcher_path = path
            self.save_settings()


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
                # 실제 Mods 폴더에 존재하는 캐릭터만 표시
        all_char_dirs = [
            d for d in os.listdir(self.wwmm_mods_path)
            if os.path.isdir(os.path.join(self.wwmm_mods_path, d))
        ]
        
        # 속성별 카테고리와 캐릭터
        categories = {
            "응결": ["카를로타", "절지", "유호", "산화", "설지" "능양"],
            "용융": ["루파", "장리", "앙코", "치샤", "브렌트", "모르테피"],
            "전도": ["음림", "상리요", "카카루", "루미", "연무"],
            "기류": ["카르티시아", "샤콘", "감심", "양양", "기염", "알토"],
            "회절": ["젠니", "페비", "파수인", "금희", "벨리나"],
            "인멸": ["칸타렐라", "로코코", "카멜리아", "도기", "단근"]
        }
        wanderer = ["방랑자"]

        category_icons = {
            "응결": "./icons/ic_응결.png",
            "용융": "./icons/ic_용융.png",
            "전도": "./icons/ic_전도.png",
            "기류": "./icons/ic_기류.png",
            "회절": "./icons/ic_회절.png",
            "인멸": "./icons/ic_인멸.png"
        }
        char_icons = {
            "방랑자": "./icons/char_방랑자.png",
            "루파": "./icons/char_루파.png",
            "카르티시아": "./icons/char_카르티시아.png",
            "샤콘": "./icons/char_샤콘.png",
            "젠니": "./icons/char_젠니.png",
            "칸타렐라": "./icons/char_칸타렐라.png",
            "페비": "./icons/char_페비.png",
            "로코코": "./icons/char_로코코.png",
            "카를로타": "./icons/char_카를로타.png",
            "카멜리아": "./icons/char_카멜리아.png",
            "파수인": "./icons/char_파수인.png",
            "절지": "./icons/char_절지.png",
            "장리": "./icons/char_장리.png",
            "금희": "./icons/char_금희.png",
            "음림": "./icons/char_음림.png",
            "벨리나": "./icons/char_벨리나.png",
            "앙코": "./icons/char_앙코.png",
            "감심": "./icons/char_감심.png",
            "브렌트": "./icons/char_브렌트.png",
            "상리요": "./icons/char_상리요.png",
            "기염": "./icons/char_기염.png",
            "카카루": "./icons/char_카카루.png",
            "능양": "./icons/char_능양.png",
            "루미": "./icons/char_루미.png",
            "유호": "./icons/char_유호.png",
            "양양": "./icons/char_양양.png",
            "산화": "./icons/char_산화.png",
            "설지": "./icons/char_설지.png",
            "치샤": "./icons/char_치샤.png",
            "단근": "./icons/char_단근.png",
            "도기": "./icons/char_도기.png",
            "모르테피": "./icons/char_모르테피.png",
            "연무": "./icons/char_연무.png",
            "알토": "./icons/char_알토.png",
            
            # ...캐릭터별 추가...
        }
        # 카테고리별 색상 딕셔너리 (참고 이미지와 유사하게)

        category_colors = {
            "응결": "#5e8ca6",   # 파랑/시원
            "용융": "#e17055",   # 빨강/주황
            "전도": "#a29bfe",   # 보라
            "기류": "#00b894",   # 녹색
            "회절": "#fdcb6e",   # 노랑
            "인멸": "#6c3483"    # 진보라/자주
        }

        # 예시: 카테고리 및 캐릭터 폰트 크기 다르게 적용
        category_font = QFont()
        category_font.setPointSize(15) # 카테고리(속성) 폰트 크기 크게
        category_font.setBold(True)

        char_font = QFont()
        char_font.setPointSize(11) # 캐릭터 폰트 일반 크기
        # 방랑자(예외)
        for char in wanderer:
            if char in all_char_dirs:
                item = QTreeWidgetItem(self.character_list, [char])
                if char in char_icons:
                    item.setIcon(0, QIcon(char_icons[char]))
                item.setFont(0, char_font)
        # 색상 변경 필요시: item.setForeground(0, QBrush(QColor("원하는색")))
        # 아니면 생략(기본색)   # 방랑자도 일반 캐릭터 폰트 크기

        # 카테고리별
        for category, char_list in categories.items():
            cat_item = QTreeWidgetItem([category])
            if category in category_icons:
                cat_item.setIcon(0, QIcon(category_icons[category]))
            cat_item.setFont(0, category_font)
            # 이 줄만 카테고리마다 다르게!
            if category in category_colors:
                cat_item.setForeground(0, QBrush(QColor(category_colors[category])))
            has_child = False
            for char in char_list:
                if char in all_char_dirs:
                    child_item = QTreeWidgetItem(cat_item, [char])
                    if char in char_icons:
                        child_item.setIcon(0, QIcon(char_icons[char]))
                    child_item.setFont(0, char_font)
                    # 캐릭터 색상 따로 하고 싶으면 아래 주석 해제
                    # child_item.setForeground(0, QBrush(QColor("#fff")))
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
        if item.childCount() > 0:
            return
        char_name = item.text(0)
        self.current_character = char_name
        char_mod_path = os.path.join(self.wwmm_mods_path, char_name)
        applied_mod = self.get_applied_mod_name(char_name)

        self.clear_mod_cards()   # 카드만 비우기

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

        # ----------- X 버튼 추가 -----------
        close_button = QPushButton("✕")
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 18px;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        
        close_button.clicked.connect(lambda _, m=mod_name: self.delete_mod(m))

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        card_layout.addLayout(header_layout)
        # -----------
        
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

    def delete_mod(self, mod_name):
        char_name = self.current_character
        if not char_name:
            return

        # 삭제 전 확인 다이얼로그
        reply = QMessageBox.question(
            self,
            "모드 삭제",
            f"정말로 [{mod_name}] 모드를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            mod_path = os.path.join(self.wwmm_mods_path, char_name, mod_name)
            try:
                if os.path.exists(mod_path):
                    shutil.rmtree(mod_path)
                    # 삭제 후 모드 카드 갱신
                    self.on_character_selected(self.find_character_item(char_name))
            except Exception as e:
                QMessageBox.critical(self, "삭제 실패", f"모드 삭제 중 오류가 발생했습니다:\n{e}")
        # 아니오면 아무 동작 없음

    def find_character_item(self, char_name):
        # 캐릭터 이름에 해당하는 QTreeWidgetItem을 반환 (카드 갱신용)
        for i in range(self.character_list.topLevelItemCount()):
            item = self.character_list.topLevelItem(i)
            # 카테고리 안에 있는 경우
            for j in range(item.childCount()):
                child = item.child(j)
                if child.text(0) == char_name:
                    return child
            # 방랑자 등 카테고리 없는 단일 캐릭터
            if item.childCount() == 0 and item.text(0) == char_name:
                return item
        return None

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