from setuptools import setup


def main():
    setup(
        name="pets-api",
        version="0.0.0",
        description="A simple Flask API for pets",
        author="Sebastian Lin",
        author_email="sebastianljs@gmail.com",
        license="MIT",
        packages=["pets_api"]
    )


if __name__ == "__main__":
    main()
