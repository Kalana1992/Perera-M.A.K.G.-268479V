from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    print("E-Commerce BI-DSS project workspace")
    print(f"Project root: {PROJECT_ROOT}")
    print("Fresh project scaffold is ready. Data pipeline modules will be implemented next.")

if __name__ == "__main__":
    main()
