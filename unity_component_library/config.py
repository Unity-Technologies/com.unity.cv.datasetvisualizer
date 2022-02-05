import setuptools

# Components
components = {
    "page_selector": {
        "dev_port": 3001
    },
    "image_selector": {
        "dev_port": 3002
    },
    "go_to": {
        "dev_port": 3003
    }
}

print(setuptools.find_packages())