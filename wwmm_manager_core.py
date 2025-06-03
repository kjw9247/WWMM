# ✅ 파일명: wwmm_manager_core.py

import os
import shutil
import subprocess
import json

# 사용자 모드 저장 위치
USER_MODS_DIR = os.path.join(os.getcwd(), "Mods")

# 설정 파일 경로
CONFIG_FILE = os.path.join(os.getcwd(), "config.json")

# 설정 불러오기
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 설정 저장
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# 윈도우 심볼릭 링크 생성
def create_symlink(src, dst):
    if os.path.exists(dst):
        if os.path.islink(dst):
            os.unlink(dst)
        else:
            shutil.rmtree(dst)
    subprocess.run(["cmd", "/c", "mklink", "/D", dst, src], shell=True)

# 캐릭터 리스트
CHARACTER_LIST = [
    "루파", "카르티시아", "샤콘", "젠니", "칸타렐라", "페비", "브렌트", "로코코", "카를로타", "카멜리아",
    "파수인", "절지", "장리", "금희", "음림", "벨리나", "앙코", "감심", "상리요", "기염",
    "카카루", "능양", "루미", "유호", "양양", "단근", "산화", "설지", "도기", "치샤",
    "모르테피", "연무", "알토", "방랑자"
]

# 사용자 모드 경로
def get_mod_path(character_name, mod_name):
    return os.path.join(USER_MODS_DIR, character_name, mod_name)

# WWMI 캐릭터 적용 경로
def get_wwmi_mods_character_path(wwmi_root, character_name):
    return os.path.join(wwmi_root, "Mods", character_name)

# 캐릭터 모드 리스트
def list_mods_for_character(character_name):
    char_dir = os.path.join(USER_MODS_DIR, character_name)
    if not os.path.exists(char_dir):
        return []
    return [mod for mod in os.listdir(char_dir) if os.path.isdir(os.path.join(char_dir, mod))]

# 선택한 모드를 심볼릭 링크로 WWMI에 적용
def apply_mod_symlink(wwmi_root, character_name, mod_name):
    """
    사용자 선택 모드를 WWMI 캐릭터 경로에 링크 방식으로 적용.
    예: Mods/장리/Yixuan → C:/WWMI/Mods/장리/Yixuan
    """
    src = get_mod_path(character_name, mod_name)
    dst_root = get_wwmi_mods_character_path(wwmi_root, character_name)
    dst = os.path.join(dst_root, mod_name)

    # 🔍 디버깅 출력
    print("✅ apply_mod_symlink 실행됨")
    print(f"character_name: '{character_name}'")
    print(f"mod_name: '{mod_name}'")
    print(f"src: {src}")
    print(f"dst: {dst}")

    if not os.path.exists(src):
        raise FileNotFoundError(f"[오류] 소스 모드 경로가 존재하지 않습니다: {src}")

    os.makedirs(dst_root, exist_ok=True)

    # 기존 링크/폴더 제거
    for item in os.listdir(dst_root):
        full_path = os.path.join(dst_root, item)
        if os.path.islink(full_path):
            os.unlink(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)

    # 새 링크 생성
    create_symlink(src, dst)

# 모드 해제 (캐릭터 단위)
def clear_mod_for_character(wwmi_root, character_name):
    dst_root = get_wwmi_mods_character_path(wwmi_root, character_name)
    if not os.path.exists(dst_root):
        return
    for item in os.listdir(dst_root):
        full_path = os.path.join(dst_root, item)
        if os.path.islink(full_path):
            os.unlink(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)