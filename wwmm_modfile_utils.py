import os
import shutil
import subprocess

# 유저 모드 저장 경로 (WWMM 내부)
USER_MODS_DIR = os.path.join(os.getcwd(), "Mods")

# 심볼릭 링크 생성 함수
def create_symlink(src, dst):
    if os.path.exists(dst):
        if os.path.islink(dst):
            os.unlink(dst)
        else:
            shutil.rmtree(dst)
    # 윈도우 전용 심볼릭 링크 생성 (관리자 권한 필요)
    subprocess.run(["cmd", "/c", "mklink", "/D", dst, src], shell=True)

# 캐릭터 이름 목록 (선언된 캐릭터들)
CHARACTER_LIST = [
    "루파", "카르티시아", "샤콘", "젠니", "칸타렐라", "페비", "브렌트", "로코코", "카를로타", "카멜리아",
    "파수인", "절지", "장리", "금희", "음림", "벨리나", "앙코", "감심", "상리요", "기염",
    "카카루", "능양", "루미", "유호", "양양", "단근", "산화", "설지", "도기", "치샤",
    "모르테피", "연무", "알토", "방랑자"
]

# 모드 경로 반환 함수
def get_mod_path(character_name, mod_name):
    return os.path.join(USER_MODS_DIR, character_name, mod_name)

# WWMI 적용 경로 설정 함수 (사용자 지정)
def get_wwmi_mods_character_path(wwmi_root, character_name):
    return os.path.join(wwmi_root, "Mods", character_name)

# 캐릭터의 모드 목록 반환
def list_mods_for_character(character_name):
    char_dir = os.path.join(USER_MODS_DIR, character_name)
    if not os.path.exists(char_dir):
        return []
    return [mod for mod in os.listdir(char_dir) if os.path.isdir(os.path.join(char_dir, mod))]

# 선택한 모드를 WWMI에 적용 (심볼릭 링크 방식)
def apply_mod_symlink(wwmi_root, character_name, mod_name):
    src = get_mod_path(character_name, mod_name)
    dst_root = get_wwmi_mods_character_path(wwmi_root, character_name)
    dst = os.path.join(dst_root, mod_name)

    os.makedirs(dst_root, exist_ok=True)

    # 기존 링크/폴더 제거
    for item in os.listdir(dst_root):
        full_path = os.path.join(dst_root, item)
        if os.path.islink(full_path) or os.path.isdir(full_path):
            if os.path.islink(full_path):
                os.unlink(full_path)
            else:
                shutil.rmtree(full_path)

    # 새 심볼릭 링크 생성
    create_symlink(src, dst)