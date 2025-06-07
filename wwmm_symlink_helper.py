# wwmm_symlink_helper.py

import os
import sys
import shutil

def create_symlink(src, dst):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    if os.path.exists(dst):
        try:
            if os.path.islink(dst):
                os.unlink(dst)
            else:
                shutil.rmtree(dst)
        except Exception as e:
            print(f"ERR:Remove {e}")
            sys.exit(1)
    try:
        os.symlink(src, dst, target_is_directory=True)
        print("OK")
        sys.exit(0)
    except Exception as e:
        print(f"ERR:Symlink {e}")
        sys.exit(1)

def remove_symlink(dst):
    dst = os.path.abspath(dst)
    if os.path.exists(dst):
        try:
            if os.path.islink(dst):
                os.unlink(dst)
            else:
                shutil.rmtree(dst)
            print("OK")
            sys.exit(0)
        except Exception as e:
            print(f"ERR:Remove {e}")
            sys.exit(1)
    else:
        print("OK")
        sys.exit(0)

def main():
    if len(sys.argv) < 3:
        print("ERR:인자 부족")
        sys.exit(1)
    mode = sys.argv[1]
    if mode == "apply":
        if len(sys.argv) != 4:
            print("ERR:apply 인자 부족")
            sys.exit(1)
        src, dst = sys.argv[2], sys.argv[3]
        create_symlink(src, dst)
    elif mode == "remove":
        if len(sys.argv) != 3:
            print("ERR:remove 인자 부족")
            sys.exit(1)
        dst = sys.argv[2]
        remove_symlink(dst)
    else:
        print("ERR:알 수 없는 명령")
        sys.exit(1)

if __name__ == "__main__":
    main()
