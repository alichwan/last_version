import json


def get_kirril_traces(filename: str) -> dict:
    """Get the traces from a file in the kirril folder

    Args:
        filename (str): string with the file to be parsed

    Returns:
        dict: traces of the form {'pos': [..], 'neg': [..]}
    """
    base_path = "./kirril_traces/"
    with open(f"{base_path}{filename}", "r", encoding="utf-8") as file:
        traces = json.load(file)
    return traces


if __name__ == "__main__":
    print(get_kirril_traces("6S5L0C.json"))
