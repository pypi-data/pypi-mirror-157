try : 
    import partinstall.array.array_test

except ImportError as e:
    msg = (
        "partinstall array requirements are not installed.\n\n"
        "Please either conda or pip install as follows:\n\n"
        '  python -m pip install "partinstall[array]" --upgrade'
    )
    raise ImportError(msg) from e