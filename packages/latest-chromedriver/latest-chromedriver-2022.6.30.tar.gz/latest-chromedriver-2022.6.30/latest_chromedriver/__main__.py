import os

import latest_chromedriver


def demo():
    # Path test
    latest_chromedriver.safely_set_chromedriver_path()
    print("\nThe Path would be transformed to:")
    print(os.environ['PATH'])


if __name__ == '__main__':
    demo()
