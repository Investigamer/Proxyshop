from re import finditer


def format_string_with_indices(
    format_string: str, **variables: object
) -> tuple[str, dict[str, list[tuple[int, int]]]]:
    """
    Format a string with named variables and track the replaced indices.

    Args:
        format_string: String with {variable_name} placeholders
        **variables: Named variables to substitute

    Returns:
        A tuple containing:
        - The formatted string
        - A dict mapping variable names to lists of (start, end) index pairs
          representing where each variable appears in the formatted string.
          The start is inclusive and the end exclusive.

    Example:
        ```
        result, indices = format_string_with_indices(
            "The {adjective} brown {animal} jumps over the lazy dog",
            adjective="quick",
            animal="fox",
        )

        # result
        "The quick brown fox jumps over the lazy dog"
        # indices
        {"adjective": [(4, 9)], "animal": [(16, 19)]}
        ```
    """
    indices_map: dict[str, list[tuple[int, int]]] = {}
    result = ""
    current_pos = 0
    last_end = 0

    # Find all named placeholders {variable_name}
    pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"

    for match in finditer(pattern, format_string):
        var_name = match.group(1)
        placeholder_start = match.start()
        placeholder_end = match.end()

        # Add the part of the string before this placeholder
        before_text = format_string[last_end:placeholder_start]
        result += before_text
        current_pos += len(before_text)

        # Get the variable value and add it to result
        if var_name in variables:
            value_str = str(variables[var_name])
            start_idx = current_pos
            result += value_str
            current_pos += len(value_str)
            end_idx = current_pos

            # Track the indices for this variable
            if var_name not in indices_map:
                indices_map[var_name] = []
            indices_map[var_name].append((start_idx, end_idx))
        else:
            full_match = match.group(0)
            result += full_match
            current_pos += len(full_match)

        last_end = placeholder_end

    # Add any remaining part of the format string
    result += format_string[last_end:]

    return result, indices_map
