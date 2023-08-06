error_substring = 'ERROR: ['


def parse_error(error_string: str):
    try:
        last_error_code_start = error_string.rindex(error_substring)
        last_error_code_start = last_error_code_start + error_substring.__len__()
        last_error_code_end = error_string.index(']', last_error_code_start)
        return error_string[last_error_code_start:last_error_code_end]
    except ValueError:
        return ''
