# Models Directory (模型存放目錄)

本目錄用於存放 YOLO 視覺檢測與圖像分割模型（支援 \.pt\ 或 \.onnx\ 格式）。

## 🤖 預設模型 (Default Model)
- **模型檔案**：\sensitive_detect_v06.pt- **模型架構**：YOLOv8-seg (Ultralytics)
- **模型作者**：[sugarknight/sensitive-detect](https://huggingface.co/sugarknight/sensitive-detect) (Hugging Face)
- **自動下載**：若從 GitHub Clone 原始碼且本目錄為空，後端啟動時將**自動自 Hugging Face 下載**本模型；亦可手動下載後放入本目錄。

## 🧩 自訂模型支援 (Custom Models)
您可以將自行訓練或微調的 YOLO 目標檢測／分割權重檔放置於本目錄，後端啟動時將自動掃描並載入於下拉選單中。
