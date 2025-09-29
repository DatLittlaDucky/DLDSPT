# Test Dependencies

import importlib
import pkg_resources

def test_installed_packages(packages):
    results = {}
    for package in packages:
        try:
            imported = importlib.import_module(package)
            version = getattr(imported, '__version__', None)
            if not version:
                try:
                    version = pkg_resources.get_distribution(package).version
                except Exception:
                    version = "Unknown"
            results[package] = f"Installed (version: {version})"
        except ImportError:
            results[package] = "Not installed"
    return results

if __name__ == "__main__":
    # List the packages you want to test here
    packages_to_test = [
        "numpy",
        "pandas",
        "matplotlib",
        "requests",
        "scipy",
        "flask",
        "django",
        "seaborn",
        "pytest",
        "beautifulsoup4",
        "sqlalchemy",
        "opencv-python",
        "Pillow",
        "tqdm",
        "plotly",
        "sklearn",
        "jupyter",
        "notebook",
        "pyyaml",
        "lxml",
        "tkinter",
        "pygame",
        "networkx",
        "sympy",
        "cryptography",
        "selenium",
        "pyinstaller",
        "pyautogui",
        "twilio",
        "paramiko",
        "boto3",
        "requests-oauthlib",
        "pytz",
        "dateutil",
        "xlrd",
        "openpyxl",
        "docx",
        "pdfminer",
        "pywin32",
        "psutil",
        "virtualenv"
    ]
    results = test_installed_packages(packages_to_test)
    missing = [pkg for pkg, status in results.items() if status == "Not installed"]
    for pkg, status in results.items():
        print(f"{pkg}: {status}")
    if missing:
        print("\nMissing packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        resp = input("\nWould you like to install all missing packages now? (y/n): ").strip().lower()
        if resp == "y":
            import subprocess
            for pkg in missing:
                print(f"Installing {pkg}...")
                try:
                    subprocess.check_call([importlib.util.find_spec("pip").origin, "install", pkg])
                except Exception as e:
                    print(f"Failed to install {pkg}: {e}")
            print("Installation complete.")
        else:
            print("You can install missing packages manually using pip.")