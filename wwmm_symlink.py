import os
import subprocess
from PyQt5.QtWidgets import QMessageBox

def create_symlink_windows_compatible(src, dst, parent_widget=None):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    if not os.path.exists(src):
        if parent_widget:
            QMessageBox.warning(parent_widget, "오류", f"원본 모드 경로가 존재하지 않습니다:\n{src}")
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        try:
            if os.path.islink(dst):
                os.unlink(dst)
            else:
                shutil.rmtree(dst)
        except Exception as e:
            if parent_widget:
                QMessageBox.warning(parent_widget, "오류", f"기존 링크 제거 실패:\n{e}")
            return
    try:
        cmd = f'mklink /D "{dst}" "{src}"'
        subprocess.call(f'cmd /c {cmd}', shell=True)
    except Exception as e:
        if parent_widget:
            QMessageBox.critical(parent_widget, "오류", f"mklink 명령 실패:\n{e}")