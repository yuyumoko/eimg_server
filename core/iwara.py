import re
from pathlib import Path

def iwara_file_handler(file: Path):
    video_id = re.findall(r"\[[a-zA-Z0-9]+\]", file.stem)
    if video_id:
        video_id = video_id[-1][1:-1]
    else:
        video_id = file.stem
    
    if re.match('^[a-zA-Z0-9]+$', video_id):
        return file, video_id
    else:
        print("->")
        print(f"Invalid file id: [{video_id}] in {file.name}")
        print("->")
    
    return file, None