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
        "lxml"
    ]
    results = test_installed_packages(packages_to_test)
    for pkg, status in results.items():
        print(f"{pkg}: {status}")