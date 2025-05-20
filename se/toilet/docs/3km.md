국토지리정보원(NGII)에서 제공하는 \*\*1km 격자 통계 데이터(SHP)\*\*를 **3km 단위 격자**로 바꾸는 것은 가능하지만, \*\*직접 재처리(aggregation)\*\*해야 합니다. 아래에 개념과 방법 정리해줄게:

---

### ✅ 1km 격자를 3km 격자로 바꾸는 방법

**전제:** 1km 격자에는 중심 좌표 또는 격자 ID가 있으며, 규칙적으로 배치되어 있음 (e.g., GID, X좌표, Y좌표)

---

### 🔧 방법 1: 좌표 기반 그룹핑

1. \*\*격자 중심 좌표(x, y)\*\*를 기준으로:

   * `x // 3000`, `y // 3000`으로 그룹핑하여 3km 블록 생성
2. 각 3km 블록 내의 1km 격자 데이터를 **sum / mean / count 등**으로 집계

📌 Python 예시 (GeoPandas + Pandas):

```python
import geopandas as gpd
import numpy as np

gdf = gpd.read_file("1km_grid.shp")

# 격자 중심 좌표 기준으로 3km 격자 단위로 그룹핑
gdf["grid_x"] = (gdf.geometry.centroid.x // 3000).astype(int)
gdf["grid_y"] = (gdf.geometry.centroid.y // 3000).astype(int)

# 3km 격자 ID 생성
gdf["grid_3km_id"] = gdf["grid_x"].astype(str) + "_" + gdf["grid_y"].astype(str)

# 그룹핑 및 합계 예시
aggregated = gdf.dissolve(by="grid_3km_id", aggfunc="sum")  # 또는 mean, count 등
```

---

### 🔧 방법 2: 공간 조인 (공식 3km 격자 SHP가 있다면)

1. **3km 격자 SHP**를 별도로 구한 후
2. `gpd.sjoin()`으로 1km 격자와 공간 조인 → 포함 관계로 매핑
3. 3km 격자 단위로 `groupby` → 합산/평균

---

### 📌 주의사항

* 격자 통계 특성상, **경계에 걸치는 값들**을 어떻게 처리할지 결정 필요 (합계 vs 평균 등)
* 꼭 좌표계(EPSG:5181 등) 확인하고 단위 맞춰야 함 (미터 단위여야 `3000`이 의미 있음)

---

### ❓ 3km 격자 SHP는 제공 안 되나?

국토지리정보원은 기본적으로 **100m / 500m / 1km 격자**만 공개합니다.
3km는 사용자가 직접 **1km 격자를 병합하여 생성**해야 합니다.

---

필요하다면, 직접 병합하는 Python 코드도 만들어줄게요. `SHP` 파일 열어보고 컬럼 확인만 해주면 됩니다.
