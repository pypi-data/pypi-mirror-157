import os


def filter(directory: str, file_types: list, blacklist_mode: bool = False):
    """
    Filters files in a directory based on their file type

    Parameters:
        directory (string): full path to the directory where the files will be filtered
        desired_file_types (list): file type extensions that will be kept, for example: [".png", ".txt"]
        blacklist_mode (bool): by default the listed file types are kept, if this is set to true, the listed file types will be removed and other remaining files will be kept

    Returns:
        void
    """

    for file_type in file_types:
        if not file_type.startswith("."):
            file_type = f".{file_type}"

    for subdir, dirs, files in os.walk(directory):

        for file in files:
            if blacklist_mode and file.endswith(tuple(file_types)):
                os.remove(f"{os.path.abspath(subdir)}/{file}")
            elif not file.endswith(tuple(file_types)):
                os.remove(f"{os.path.abspath(subdir)}/{file}")


if __name__ == "__main__":
    filter("C:/Users/ambl/Downloads/filter_test/", [".png", ".txt", "md"])
