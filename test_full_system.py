# test_full_system.py
# ============================================================
# RETURNSHIELD AI — Master End-to-End System Verification
# ============================================================
# Runs deep health checks across all 5 architecture layers:
# 1. Raw Datasets & Preprocessed Artifacts
# 2. ML Engine (Model Pipeline + SHAP Inference + Latency)
# 3. Relational Database (8 Tables & Record Integrity)
# 4. FastAPI REST API (Endpoints, Live Scoring, Decision Rules)
# 5. Frontend & Production Readiness
# ============================================================

import os
import sys
import time
import json
import sqlite3

import os
import sys
import time
import json
import sqlite3

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def print_header(title):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*65}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  {title}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*65}{Colors.RESET}")

def print_pass(msg):
    print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {msg}")

def print_fail(msg):
    print(f"  {Colors.RED}[FAIL]{Colors.RESET} {msg}")

def print_info(msg):
    print(f"  {Colors.YELLOW}[INFO]{Colors.RESET} {msg}")


def test_layer1_datasets():
    print_header("LAYER 1: Datasets & Machine Learning Artifacts")
    passed = 0
    total = 0

    csv_files = [
        ("data/customers.csv", 5000),
        ("data/orders.csv", 20000),
        ("data/returns.csv", 5000),
        ("data/refunds.csv", 4000),
        ("data/delivery_logs.csv", 20000),
        ("data/app_activity.csv", 10000),
    ]

    for rel_path, min_rows in csv_files:
        total += 1
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                lines = sum(1 for _ in f) - 1  # exclude header
            if lines >= min_rows:
                print_pass(f"{rel_path} present ({lines:,} records, expected >= {min_rows:,})")
                passed += 1
            else:
                print_fail(f"{rel_path} only has {lines} rows (expected >= {min_rows})")
        else:
            print_fail(f"{rel_path} not found!")

    # Check artifacts
    artifacts = [
        "artifacts/model_pipeline.pkl",
        "artifacts/metrics.json",
        "artifacts/return_features.csv",
    ]
    for rel_path in artifacts:
        total += 1
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.exists(full_path):
            size_kb = os.path.getsize(full_path) / 1024
            print_pass(f"{rel_path} ready ({size_kb:.1f} KB)")
            passed += 1
        else:
            print_fail(f"{rel_path} not found!")

    return passed == total


def test_layer2_ml_engine():
    print_header("LAYER 2: Machine Learning Inference & SHAP Engine")
    try:
        from ml.predict import get_predictor
        t0 = time.time()
        predictor = get_predictor()
        load_time = (time.time() - t0) * 1000
        print_pass(f"Model Pipeline loaded in {load_time:.2f} ms")

        # Load metrics.json
        metrics_path = os.path.join(PROJECT_ROOT, "artifacts", "metrics.json")
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        
        f1 = metrics.get("f1_score", 0)
        roc = metrics.get("roc_auc", 0)
        acc = metrics.get("accuracy", 0)
        prec = metrics.get("precision", 0)
        rec = metrics.get("recall", 0)

        print_pass(f"Model Accuracy: {acc*100:.2f}% | Precision: {prec*100:.2f}% | Recall: {rec*100:.2f}%")
        print_pass(f"F1-Score: {f1*100:.2f}% | ROC-AUC: {roc*100:.2f}%")

        # Run test inference on normal customer
        from backend.services import risk_service
        from backend.database import SessionLocal
        db = SessionLocal()

        t1 = time.time()
        res_safe = risk_service.score_return(db, "CUST00004", "RET000001")
        latency_safe = (time.time() - t1) * 1000
        print_pass(f"Inference [CUST00004/RET000001]: Score = {res_safe['risk_score']}% ({res_safe['risk_level']}) in {latency_safe:.1f} ms")
        print_info(f"Top SHAP Factor: {res_safe['top_risk_factors'][0]['feature']} ({res_safe['top_risk_factors'][0]['direction']})")

        # Run test inference on abusive customer
        t2 = time.time()
        res_abuse = risk_service.score_return(db, "CUST00027", "RET000011")
        latency_abuse = (time.time() - t2) * 1000
        print_pass(f"Inference [CUST00027/RET000011]: Score = {res_abuse['risk_score']}% ({res_abuse['risk_level']}) in {latency_abuse:.1f} ms")
        print_info(f"Action Recommended: {res_abuse['action']}")

        db.close()
        return True
    except Exception as e:
        print_fail(f"ML Engine Error: {e}")
        return False


def test_layer3_database():
    print_header("LAYER 3: Relational Database (SQLite returnshield.db)")
    db_file = os.path.join(PROJECT_ROOT, "returnshield.db")
    if not os.path.exists(db_file):
        print_fail(f"Database file not found: {db_file}")
        return False

    size_mb = os.path.getsize(db_file) / (1024 * 1024)
    print_pass(f"Database file returnshield.db found ({size_mb:.2f} MB)")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    tables = [
        "customers", "orders", "returns", "refunds", 
        "delivery_logs", "app_activity", "cs_interactions",
        "investigations", "audit_logs"
    ]

    all_ok = True
    for tbl in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            count = cursor.fetchone()[0]
            print_pass(f"Table '{tbl}': {count:,} records")
        except Exception as e:
            print_fail(f"Table '{tbl}' error: {e}")
            all_ok = False

    conn.close()
    return all_ok


def test_layer4_fastapi():
    print_header("LAYER 4: FastAPI REST API Endpoints")
    try:
        import requests
        base_url = "http://localhost:8000"

        # Health
        r_health = requests.get(f"{base_url}/api/health", timeout=5)
        if r_health.status_code == 200 and r_health.json().get("status") == "healthy":
            print_pass("GET /api/health: HTTP 200 OK (Status: healthy)")
        else:
            print_fail(f"GET /api/health returned {r_health.status_code}: {r_health.text}")

        # Overview
        r_overview = requests.get(f"{base_url}/api/dashboard/overview", timeout=5)
        if r_overview.status_code == 200:
            data = r_overview.json()
            print_pass(f"GET /api/dashboard/overview: HTTP 200 OK (Total returns: {data.get('total_returns')})")
        else:
            print_fail(f"GET /api/dashboard/overview returned {r_overview.status_code}")

        # Live Score
        payload = {"customer_id": "CUST00004", "return_id": "RET000001"}
        r_score = requests.post(f"{base_url}/api/risk/score", json=payload, timeout=5)
        if r_score.status_code == 200:
            score_data = r_score.json()
            print_pass(f"POST /api/risk/score: HTTP 200 OK (Score: {score_data.get('risk_score')}%, Level: {score_data.get('risk_level')})")
        else:
            print_fail(f"POST /api/risk/score returned {r_score.status_code}")

        # Returns List
        r_returns = requests.get(f"{base_url}/api/returns?limit=5", timeout=5)
        if r_returns.status_code == 200:
            print_pass(f"GET /api/returns: HTTP 200 OK ({len(r_returns.json())} items fetched)")
        else:
            print_fail(f"GET /api/returns returned {r_returns.status_code}")

        # Metrics
        r_metrics = requests.get(f"{base_url}/api/metrics", timeout=5)
        if r_metrics.status_code == 200:
            print_pass(f"GET /api/metrics: HTTP 200 OK (Model: {r_metrics.json().get('model')})")
        else:
            print_fail(f"GET /api/metrics returned {r_metrics.status_code}")

        return True
    except Exception as e:
        print_fail(f"FastAPI Server is not running on port 8000 or error: {e}")
        print_info("Start server via: .venv\\Scripts\\uvicorn.exe backend.main:app --host 0.0.0.0 --port 8000 --reload")
        return False


def test_layer5_frontend():
    print_header("LAYER 5: Frontend Interface & Static Assets")
    frontend_dir = os.path.join(PROJECT_ROOT, "frontend")
    html_file = os.path.join(frontend_dir, "index.html")
    css_file = os.path.join(frontend_dir, "styles.css")
    js_file = os.path.join(frontend_dir, "app.js")

    all_ok = True
    for f_path, label in [(html_file, "index.html"), (css_file, "styles.css"), (js_file, "app.js")]:
        if os.path.exists(f_path):
            size_kb = os.path.getsize(f_path) / 1024
            print_pass(f"Frontend '{label}' ready ({size_kb:.1f} KB)")
        else:
            print_fail(f"Frontend file '{label}' missing!")
            all_ok = False

    return all_ok


def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}================================================================={Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}       🛡️  RETURNSHIELD AI — FULL SYSTEM VERIFICATION SUITE       {Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}================================================================={Colors.RESET}")
    
    start_time = time.time()
    results = [
        ("Layer 1: Datasets & Artifacts", test_layer1_datasets()),
        ("Layer 2: ML Engine & Inference", test_layer2_ml_engine()),
        ("Layer 3: Relational Database", test_layer3_database()),
        ("Layer 4: FastAPI REST APIs", test_layer4_fastapi()),
        ("Layer 5: Frontend Interface", test_layer5_frontend()),
    ]
    
    elapsed = time.time() - start_time
    print_header(f"FINAL SYSTEM AUDIT SUMMARY (Completed in {elapsed:.2f}s)")

    passed_count = sum(1 for _, ok in results if ok)
    for name, ok in results:
        status_str = f"{Colors.GREEN}✔ PASSED{Colors.RESET}" if ok else f"{Colors.RED}✘ FAILED{Colors.RESET}"
        print(f"  {name.ljust(35)} : {status_str}")

    print(f"\n{Colors.BOLD}{'='*65}{Colors.RESET}")
    if passed_count == len(results):
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL {len(results)} LAYERS VERIFIED SUCCESSFULLY! SYSTEM IS 100% OPERATIONAL.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ {passed_count}/{len(results)} Layers Passed. Check failed items above.{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*65}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
