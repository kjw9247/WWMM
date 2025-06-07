# wwmm_start.py

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFontDatabase, QFont
from wwmm_symlink import create_symlink_windows_compatible
from wwmm_mod_utils import is_admin, run_as_admin

from wwmm_ui import WWMM  # ← 이제 여기서 WWMM을 import

if __name__ == "__main__":
    if '--apply-mod' in sys.argv:
        idx = sys.argv.index('--apply-mod')
        char_name = sys.argv[idx + 1]
        mod_name = sys.argv[idx + 2]

        # <--- 이 부분 추가!!
        # settings에서 WWMI 경로 읽기
        from wwmm_settings import load_settings
        settings_file = os.path.join(os.getcwd(), "settings.json")
        wwmi_mods_path, character_order, xxmi_launcher_path = load_settings(settings_file)
        # WWMM 경로는 프로젝트 루트 기준으로 사용
        wwmm_mods_path = os.path.abspath(os.path.join(os.getcwd(), "Mods"))

        from wwmm_symlink import create_symlink_windows_compatible
        from wwmm_mod_utils import is_admin, run_as_admin

        if not is_admin():
            run_as_admin(
                sys.executable,
                sys.argv
            )
            sys.exit(0)
        selected_mod_path = os.path.join(wwmm_mods_path, char_name, mod_name)
        target_path = os.path.join(wwmi_mods_path, char_name)
        create_symlink_windows_compatible(selected_mod_path, target_path, None)
        from PyQt5.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        QMessageBox.information(None, "완료", "모드가 적용되었습니다. WWMM을 다시 시작합니다.")
        import subprocess
        subprocess.Popen([sys.executable, sys.argv[0]])
        sys.exit(0)
        

    import ctypes
    myappid = 'wwmm.modmanager.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    font_path = os.path.join(os.getcwd(), "./font/AstaSans-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(family, 13))
    else:
        print("AstaSans 폰트 로드 실패")

    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255,255,255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(255,255,255))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255,255,255))
    dark_palette.setColor(QPalette.Text, QColor(255,255,255))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255,255,255))
    dark_palette.setColor(QPalette.BrightText, QColor(255,0,0))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0,0,0))
    app.setPalette(dark_palette)

    window = WWMM()
    window.show()
    sys.exit(app.exec_())