# scripts/stock_main.py
"""
주식 시황 브리핑 자동화 진입점 (GitHub Actions 백업 경로).
- 중복 코드 타파를 위해 scripts/run_stock.py를 직접 기동하도록 랩핑합니다.
- 전역 SSL 비활성화 취약점이 안전하게 영구 제거되었습니다.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.run_stock import main

if __name__ == "__main__":
    main()
