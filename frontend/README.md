# 🎨 ReturnShield AI — Frontend Dashboard

ReturnShield AI ka frontend ek modern, responsive aur glassmorphic **Single-Page Application (SPA)** hai jo e-commerce merchants ko real-time return abuse analysis, visual alerts, aur policy recommendations provide karta hai.

---

## 📁 Folder Structure

```text
frontend/
├── index.html       # Semantic HTML5 single-page application structure
├── styles.css       # Razorpay-inspired dark glassmorphism design tokens & animations
├── app.js           # Client-side logic, API calls, Chart.js integrations & persona presets
└── README.md        # Yeh documentation file
```

---

## 🌟 Key Features

1. **Live Risk Simulator & Personas**:
   - 1-Click persona presets:
     - 🟢 **Safe VIP Shopper** (Zero false alarm)
     - 🟡 **Occasional Exchanger** (Normal sizing exchange)
     - 🔴 **Serial Wardrober** (Wears & returns late)
     - 🚨 **Device Farm Abuser** (Multiple accounts on single device)
   - Interactive range sliders for Return Rate, Refund Drain Ratio, aur Return Lag.
   - Real-time animated **SVG Radial Risk Gauge** (0 to 100%).

2. **Policy Enforcement Advisory Engine**:
   - Automated merchant actions:
     - `LOW RISK`: **1-Click Instant Refund** (VIP frictionless experience)
     - `MEDIUM RISK`: **3PL Barcode Verification** (Standard return checks)
     - `CRITICAL RISK`: **Hold Refund / Require Unboxing Video & Hub Inspection**

3. **Benchmarking & Model Governance Tab**:
   - Interactive bar chart (Chart.js) comparing **6 ML algorithms** (XGBoost, Random Forest, Gradient Boosting, etc.).
   - Key evaluation metrics: Accuracy, Precision, Recall, aur F1-Score.

4. **Customer Audit Explorer**:
   - Real customer database audit table with live search by ID, City, or Category.
   - Filter by "Abusive Only" ya "Normal Only".
   - Har customer row par **Audit &rarr;** button jo unka data directly simulator me load karke live predict karta hai!

---

## 🚀 How to Run the Frontend

Frontend ko run karne ke 2 aasan tareeqe hain:

### Tareeqa 1: Python HTTP Server (Recommended)
Project ke terminal me run karein:
```bash
# Frontend folder ke andar ya project root se:
python -m http.server 3000 --directory frontend
```
Browser me open karein:
👉 [http://localhost:3000](http://localhost:3000)

### Tareeqa 2: VS Code Live Server Extension
1. VS Code me `frontend/index.html` file open karein.
2. Bottom-right me **"Go Live"** button par click karein (ya right-click -> `Open with Live Server`).
3. Browser automatically open ho jayega (`http://127.0.0.1:5500/frontend/index.html`).

---

## 🔗 Backend Connection

- Frontend by default `http://127.0.0.1:8000` par run ho rahe FastAPI microservice se connect hota hai.
- Agar backend online hai, toh top-right me **Green indicator** (`API Online (Port 8000)`) dikhega.
- Agar backend offline hai, toh UI freeze nahi hoga; automatically **smart fallback heuristic simulation mode** me switch ho jayega taaki aap hackathon demo me bina kisi rukawat ke show kar sakein!
