from pathlib import Path

from deploydocus.__main__ import gen_app

cur_file = Path(__file__)
env_file_path = cur_file.parent / ".env"

ret = gen_app(env_file=env_file_path)
