import argostranslate.package

argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()

for pkg in available_packages:
    print(pkg.from_code, "->", pkg.to_code)
