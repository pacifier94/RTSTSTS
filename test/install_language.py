import argostranslate.package
import argostranslate.translate

# update package index
argostranslate.package.update_package_index()

available_packages = argostranslate.package.get_available_packages()

# install Hindi → English and English → Bengali
for pkg in available_packages:
    if (pkg.from_code == "hi" and pkg.to_code == "en") or \
       (pkg.from_code == "en" and pkg.to_code == "bn"):
        print(f"Installing {pkg.from_code} → {pkg.to_code}")
        argostranslate.package.install_from_path(pkg.download())