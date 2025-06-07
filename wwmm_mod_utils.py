import os
import shutil
import ctypes

def is_admin():
    """현재 프로세스가 관리자 권한인지 반환 (Windows Only)"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin(exe_path, params):
    """
    관리자 권한으로 exe_path를 실행한다.
    params는 리스트거나 문자열이어야 한다.
    """
    if isinstance(params, list):
        params = " ".join([f'"{arg}"' for arg in params])
    # runas: 관리자 권한
    return ctypes.windll.shell32.ShellExecuteW(
        None, "runas", exe_path, params, None, 1)

def add_mod_folder(char_name, folder, wwmm_mods_path, on_character_selected, find_character_item, parent_widget):
    if not char_name:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(parent_widget, "오류", "캐릭터를 먼저 선택하세요.")
        return
    if not folder:
        return
    mod_folder_name = os.path.basename(folder.rstrip("/\\"))
    target_dir = os.path.join(wwmm_mods_path, char_name, mod_folder_name)
    if os.path.exists(target_dir):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(parent_widget, "오류", "같은 이름의 모드가 이미 존재합니다.")
        return
    try:
        shutil.copytree(folder, target_dir)
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(parent_widget, "성공", f"모드가 추가되었습니다: {mod_folder_name}")
        on_character_selected(find_character_item(char_name))
    except Exception as e:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(parent_widget, "실패", f"모드 복사 중 오류:\n{e}")

def delete_mod(char_name, mod_name, wwmm_mods_path, on_character_selected, find_character_item, parent_widget):
    if not char_name:
        return
    mod_path = os.path.join(wwmm_mods_path, char_name, mod_name)
    try:
        if os.path.exists(mod_path):
            shutil.rmtree(mod_path)
            on_character_selected(find_character_item(char_name))
    except Exception as e:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(parent_widget, "삭제 실패", f"모드 삭제 중 오류가 발생했습니다:\n{e}")

        
def get_preview_image_path(mod_path):
    # preview.(png|jpg|jpeg 등) 파일만 찾음
    for ext in ('png', 'jpg', 'jpeg', 'bmp', 'gif'):
        p = os.path.join(mod_path, f'preview.{ext}')
        if os.path.exists(p):
            return p
    return None

#def get_preview_image_path(mod_path):
#    candidates = glob.glob(os.path.join(mod_path, "Preview.*"))
#   return os.path.abspath(candidates[0]) if candidates else None 