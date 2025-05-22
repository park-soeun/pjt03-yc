from pathlib import Path
import pandas as pd
import matplotlib as mpl
import matplotlib.font_manager as fm

app_dir = Path(__file__).parent

font_path = app_dir / "MaruBuri-Regular.ttf"
font_prop = fm.FontProperties(fname=font_path)

# 마이너스 깨짐 방지
mpl.rcParams["axes.unicode_minus"] = False
