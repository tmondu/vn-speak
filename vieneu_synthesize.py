import sys
import os
import argparse

# Automatically add venv site-packages if run with system python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
venv_lib_dir = os.path.join(BASE_DIR, "venv", "lib")
if os.path.exists(venv_lib_dir):
    for py_ver in sorted(os.listdir(venv_lib_dir), reverse=True):
        sp = os.path.join(venv_lib_dir, py_ver, "site-packages")
        if os.path.isdir(sp) and sp not in sys.path:
            sys.path.insert(0, sp)

from vieneu import Vieneu

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    tts = Vieneu(mode="v3nano")
    audio = tts.infer(text=args.text, voice=args.voice)
    tts.save(audio, args.out)

if __name__ == "__main__":
    main()
