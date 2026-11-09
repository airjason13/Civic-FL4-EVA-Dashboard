# 2023 Honda Civic e:HEV (FL4) Cyberpunk OBD2 Dashboard

專為 **2023 Honda Civic e:HEV (FL4 油電版)** 與 **樹莓派 Linux** 開發的高性能賽博龐克風格數位儀表板。

---

## 🌟 核心特色

1. **雙重極致視覺風格（EVA 新世紀福音戰士 vs. 賽博龐克）**：
   * **EVA 式樣（綾波零 Rei Ayanami 駕駛艙主題，預設啟動）**：
     * **左側面板**：
       * **2D 綾波零（Rei Ayanami）**：身穿零號機白色作戰服座於 Entry Plug 駕駛艙內，具備即時待機呼吸浮動、微幅姿態擺動、L.C.L. 全像雷射掃描線、底部八角形 A.T. FIELD 展開脈衝基座與跳動音訊等化器。
       * **專屬綾波零語音台詞**：根據車輛油電狀態觸發沉著冷靜的 EVA 反應台詞（如：「A.T.力場全開！出力限制器解除……衝刺」、「動能回路啟動，內部電源充填中」、「內部電源運作中，神經迴路無異常」等）。
       * **活動限界計時大電槽**：EV 純電模式顯示 `INTERNAL BATTERY [04:59] // 活動限界`；引擎啟動發電時切換為 `UMBILICAL CABLE: CONNECTED // 外部電源直連`。
       * **示波儀表**：大電電壓、模組溫度與 `LCL STATUS: PURIFIED | SYNCHRO: 94.8%` 同步率監控。
     * **中央儀表**：
       * **八角形 A.T. FIELD（絕對恐怖領域）G 力雷達**：同心八角力場屏障、雷達錐形掃描線、鎖定準星，劇烈過彎時力場壓縮並觸發警戒文字 `[ ! A.T. FIELD ! COMPRESSION ]`。
     * **右側與頂部/底部**：
       * **MAGI-01 系統遙測面板**：冷卻水溫、12V 輔助電瓶電壓、NERV 橙/酸性綠多段式 LED 油門開度與馬達輸出電平表。
       * **頂底戰術 HUD**：`MAGI-01 SYSTEM LIVE` 心跳燈、`SECURITY: A-17 // SOUND ONLY`、`EVA-00 // FL4 e:HEV` 戰術代號。
   * **賽博龐克風格（Cyberpunk Race Queen）**：
     * 經典雙馬尾高科技賽車女郎、賽博高壓大電條與摩擦力圓 G 力儀。
   * **一鍵切換**：按下鍵盤 `T` 鍵即可在 **EVA 綾波零** 與 **賽博龐克賽車女郎** 之間無縫即時切換！

2. **100% 防亮故障燈安全機制**：
   * **協議強制鎖死**：`AT SP 6`（直接鎖定 ISO 15765-4 11-bit 500k，嚴禁自動盲掃引發 CAN Bit Errors）。
   * **點對點單播尋址**：`AT SH 7E0`（引擎 ECM）與 `AT SH 7E2`（油電 PCU），絕不發送 `0x7DF` 廣播，不驚動煞車/VSA 防滑電腦。
   * **非同步節流**：指令間保留 25ms 冷卻時間，總通訊量佔車載 CAN 頻寬 < 3%。
   * **熄火自動靜音**：連續偵測到 `NO DATA` 時主動停止查詢，不干擾車輛休眠。

3. **內建模擬器（Mock Simulator）**：
   * 即使不在車上，在電腦桌前也能一鍵啟動擬真加減速、動能回充、大電充放循環與 G 值波動測試。

---

## 🚀 快速啟動

### 1. 桌面端測試（模擬器模式）
```bash
# 預設啟動 EVA 綾波零風格
python3 main.py --mock

# 指定主題啟動（'eva' 或 'cyberpunk'）
python3 main.py --mock --theme eva
python3 main.py --mock --theme cyberpunk
```

### 2. 實車連線（搭配 OBDLink EX / MX+）
```bash
# 有線 USB (OBDLink EX)
python3 main.py --port /dev/ttyUSB0

# 藍牙 SPP (OBDLink MX+)
python3 main.py --port /dev/rfcomm0

# 全螢幕運行
python3 main.py --port /dev/ttyUSB0 --fullscreen
```

---

## ⌨️ 鍵盤快捷鍵
* `T`：**無縫切換主題**（EVA 綾波零 NERV MAGI ⇄ 賽博龐克賽車女郎）
* `F11`：切換全螢幕 / 視窗模式
* `M`：隨時在「實車 OBD 連線」與「擬真模擬器」之間快速切換
* `Esc` / `Q`：優雅關閉離開

---

## 🚗 樹莓派車載配置建議（防止斷電壞卡）
在樹莓派終端機執行：
```bash
sudo raspi-config
```
依序進入：`Performance Options` -> `Overlay File System` -> 選擇 **Enable**。
開啟唯讀檔案系統後，車輛熄火即使突然斷電拔插頭，microSD 卡與系統也 100% 不會損壞！
