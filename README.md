# 紳士打碼 Next (Gentleman-Mosaic-Next) v2.4.0

- **當前維護者**: [Chaos2-lgtm](https://github.com/Chaos2-lgtm/Gentleman-Mosaic-Next) (Next 版)
- **直接源自專案**: [yuuhouse/Gentleman-Mosaic-forge](https://github.com/yuuhouse/Gentleman-Mosaic-forge) (Forge 再版)
- **初始原創專案**: [leeprinxin/Gentleman-Mosaic](https://github.com/leeprinxin/Gentleman-Mosaic) (最初原版)
- **授權條款 (License)**: MIT

## 專案沿革與致謝
本專案為開源社群傳承與現代化重構版本，特別感謝歷任開發者的心血結晶：
1. **最初原創**：[leeprinxin/Gentleman-Mosaic](https://github.com/leeprinxin/Gentleman-Mosaic) —— 奠定「小畫家式塗抹＋單層套用」的核心體驗與直覺設計。
2. **二次開發 (Forge 版)**：[yuuhouse/Gentleman-Mosaic-forge](https://github.com/yuuhouse/Gentleman-Mosaic-forge) —— 本專案由此版本 Fork 而來，優化了 UI 比例與即時筆刷效能。
3. **Next 版 (本專案)**：[Chaos2-lgtm/Gentleman-Mosaic-Next](https://github.com/Chaos2-lgtm/Gentleman-Mosaic-Next) —— 於 v2.4.0 進行全面現代化架構升級，加入本機獨立 AI (YOLO-seg) 實例分割精確塗抹、0 相依獨立免安裝發布包、深淺主題切換。

> **AI 技術致謝**：本專案 AI 視覺功能由 [Ultralytics](https://github.com/ultralytics/ultralytics) 的 YOLO 技術基礎提供支援（AI 模型推論基於社群開源預訓練權重）。

## 開發 / Vibe Coding 工具
- **Google Antigravity**：接手後（v2.4.0+）全端架構重構、本地獨立 AI (YOLO-seg) 模型整合、外觀主題系統與 0 相依獨立懶人發布包打包。
- **Git**：用於比對版本差異、追蹤版本變更與版本發布。
- **Chrome Headless**：用於執行 Canvas 操作體驗 benchmark，換算 FPS 與效能差異。

![紳士打碼 Logo](./assets/logo-Photoroom.png)

## 介面預覽
![UI Demo](./assets/UI.PNG)
![輸出示意圖](./assets/mosaic-output_GentlemanMosaic.png)

### v2.4.0 (AI Next)
- **本地獨立 AI 自動偵測敏感部位**：整合 Ultralytics YOLOv8/v11 引擎與 `sensitive_detect_v06.pt` 高精度模型，支援本機 GPU (CUDA) 極速推論，完全擺脫 ComfyUI 依賴。
- **精確塗抹 vs 矩形框選**：支援實例分割多邊形（YOLO-seg），AI 偵測直接貼合器官真實邊緣精確塗抹（預設），並可隨時手動以畫布筆刷（加選 / 減選）微調。
- **自訂部位篩選**：支援 4 大敏感目標部位勾選（女性私密處、男性私密處、胸部／乳頭、臀部／肛門）。
- **敏感度動態拉條**：提供 0.01 ～ 1.00 敏感度閾值即時調節（預設 0.25），數值即時連動反饋。
- **外觀主題三合一**：支援白色模式、深色模式以及隨系統自動切換（預設隨系統），並新增左上角一鍵快速輪播切換鈕。
- **完整雙語系支援**：介面各控制項、AI 面板、狀態提示及模型名稱全面支援繁體中文與 English 即時切換。
- **專屬目錄動態掃描**：後端嚴格僅掃描專案目錄 `models/`，放入模型即時生效，絕不影響外部環境。
- **0 相依獨立懶人發布包**：單鍵啟動，免裝 Python、免裝 ComfyUI，壓縮後低於 2GB 完美適配 GitHub Releases。

### v2.3.2 
- 本次更新基於最新提交 `02ac597`：Overlay canvas for cursor & live-stroke
- 新增 overlay canvas，用於游標與即時塗抹筆跡顯示
- 改善因為2.3.1調整導致的效能下降
  
### v2.3.1 
- 壓縮整體 UI 尺寸，減少側欄、工具列、縮圖列與預覽欄佔用空間
- 放寬圖片自動適合視窗縮放下限，瀏覽器 100% 縮放下也更容易完整檢視大圖

### v2.3.0 
- 修復筆刷超出畫布時會停止塗抹的問題
- 調整 UI 比例，讓瀏覽器內可以完整顯示 4K 圖片
- 新增批次下載已完成打碼圖片功能
- 整理資料夾結構，提升可讀性與後續維護性
- 新增 `config/` 與 `assets/`，將 `launch.ini`、`runtime-config.js` 與示意圖片分門別類存放
- 將 archive 目錄進一步細分為 `archive/legacy` 和 `archive/docs`

### v2.2.0 4K 大圖效能升級
- 針對 4K / 高解析圖片操作重新優化：框選、塗抹、滑鼠 hover 不再反覆重算整張圖片。
- 效果預覽加入快取機制，只有選區、效果參數或圖片內容改變時才更新，大幅降低拖曳時的卡頓感。
- Canvas 重繪改用 `requestAnimationFrame` 節流，操作節奏更貼近螢幕刷新率，筆刷移動更順。
- 大圖歷史紀錄會自動控制快照數量，避免 4K 圖片連續 Undo/Redo 時吃爆記憶體。
- 仍保留完整解析度輸出：互動變順，不犧牲下載成品品質。

### 最新版v2.3.0 vs v2.1.0 操作體驗 FPS 比較

測試方式：使用本機 Chrome Headless 量測 `standalone.html` 核心 Canvas 流程，模擬圖片中 60% 區域套用馬賽克；操作體驗 FPS 以「預覽內容未變更時反覆 render」換算，並以常見螢幕刷新率 60fps 作為上限。測試檔位於 `tools/perf-compare-v210-v230.html`。

| 情境 | v2.1.0 | 最新版 | 操作體驗差異 |
|---|---:|---:|---:|
| 1080p 預覽未變更時操作 | 60fps | 60fps | 約 0% |
| 4K 預覽未變更時操作 | 約 14.3fps | 60fps | 約 +319% |

補充：真正按下「確定套用」時，兩版馬賽克演算法耗時接近；最新版主要提升的是拖曳、hover、選取後預覽未變更時的互動流暢度，尤其是 4K 圖片。

### v2.1.0 
- 設定面板改為右上角 icon（齒輪）
- 新增關於我 icon，並改為彈跳視窗（可按 `X`、遮罩、`Esc` 關閉）
- 語言與 Dark/Light 設定可寫入 `launch.ini` 並於下次啟動自動套用
- 新增選取方向切換：正向 / 反向
- 新增選取操作切換：加選 / 減選
- 新增快捷鍵：`Ctrl+Z` / `Ctrl+Shift+Z` / `Ctrl+Y` / `Ctrl+X`、`Space+左鍵拖移`
- 歷史回溯修正：Undo/Redo 可正確回復當次提示區域（待處理區域）
- 馬賽克演算法修正，顆粒效果對齊 [PEKO-STEP](https://www.peko-step.com/tool/imageeditor/index.php?lang=zhtw&type=19) 風格
- 圖片檢視優化：支援拖移平移檢視
- 深色模式配色優化，特別是中間圖片區塊網底更柔和

### v2.0.0 
- 批次上傳與圖片切換（最多 30 張）
- 每張圖片各自保存：待處理區域、歷史回溯（Undo/Redo）
- 縮圖右鍵選單：刪除圖片、下載該圖處理後結果
- 縮圖快捷選取：左鍵選擇、`Ctrl + 左鍵` 多選、`Shift + 左鍵` 區間選取、`Ctrl + A` 全選
- 支援 NSFW 自動偵測（NudeNet）：可調偵測閾值、模型 `320n` / `640m`
- 打碼方式：馬賽克、海苔（顏色、透明度、寬度、間隔、方向可調）
- 選取模式：框選、塗抹（圓形/方形筆刷）
- 支援深色模式與中英文介面切換

## 系統需求
- Windows（含 `.bat` 啟動流程）
- Python 3.9+（建議 3.10+）
- 可連網下載 Python 套件（第一次啟動時）

## 安裝與啟動（建議）

### 一鍵啟動（Standalone）
1. 進入專案根目錄。
2. 確認有下列檔案：`start_app.bat`、`config/launch.ini`、`standalone.html`。
3. 直接雙擊 `start_app.bat`。
4. 腳本會自動讀取設定、建立 `.venv`、安裝依賴、啟動後端，並開啟 `standalone.html`。

### `config/launch.ini` 主要設定
```ini
[backend]
enabled=1
use_venv=1
venv_dir=.venv
create_venv=1
python_cmd=python
host=127.0.0.1
port=7400
reload=0
auto_install_deps=1
```

說明：
- `port` 會同步寫入 `config/runtime-config.js`，前端會使用該埠連線後端。
- 想關閉後端可設 `enabled=0`（僅做手動打碼編輯）。

## 開發模式（Standalone/Vite）
```bash
npm install
npm run dev
```

開啟：
```text
http://localhost:5173/standalone.html
```

注意：目前正式功能集中在 `standalone.html`。`src/App.jsx` 是早期/簡化 React 版本，沒有批次、NSFW 偵測、海苔、語言與主題設定等完整功能。

## 使用流程
1. 批次上傳圖片或拖曳圖片到畫布區。
2. 在上方縮圖列選擇要編輯的圖片。
3. 選擇打碼效果（馬賽克 / 海苔）。
4. 用框選或塗抹建立待處理區域。
5. 按「確定套用」完成本次打碼。
6. 需要時可用 Undo / Redo 回溯。
7. 右鍵縮圖可刪除或下載處理後圖片。

## 注意事項
- 第一次啟動會下載 Python 套件，時間較久屬正常。
- 若 Python 指令不是 `python`，可在 `launch.ini` 調整 `python_cmd`。
- 批次上限為 30 張，超過會提示並忽略多餘檔案。
