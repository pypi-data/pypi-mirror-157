import os


class SelfRelease:
    """
    Class responsible to serve the library in pypi, not part of rocket executable
    """

    """Module responsible for building db-rocket itself and publishing it to pypi"""

    def build(self):
        """
        Build rocket for pypi. Run it on the root of rocket project.
        """
        os.system("rm -rf dist/* || true")
        os.system("python3 -m build")

    def release(self):
        """
        Build rocket for pypi. Run it on the root of rocket project.
        """
        os.system("rm -rf dist/* || true")
        os.system("python3 -m build --no-isolation")
        print("Build successfull, uploading now")
        self.upload()

    def upload(self):
        """
        Upload new package to pipy
        :return:
        """
        os.system("python3 -m twine upload dist/*")
