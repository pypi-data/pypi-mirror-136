def build_dummy_list(unique_values: list, selected_item: str) -> list:
    """
    Builds a dummy list with the selected item as 1 and the rest as 0.
    unique_values: list of unique values in the column
    selected_item: the item to be selected
    return: list of 0s and 1s
    """
    dummy_list = [0 for _ in range(len(unique_values))]
    dummy_list[unique_values.index(selected_item)] = 1
    return dummy_list
