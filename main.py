# main.py — GitHub Actions 호환 진입점 (shim → scripts/run_news.py)
from scripts.run_news import main
if __name__ == "__main__":
    main()
