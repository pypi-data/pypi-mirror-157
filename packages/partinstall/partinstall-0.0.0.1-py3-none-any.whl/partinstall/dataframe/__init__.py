try : 
    import partinstall.dataframe.dataframe_test

except ImportError as e:
    msg = (
        "partinstall dataframe requirements are not installed.\n\n"
        "Please either conda or pip install as follows:\n\n"
        '  python -m pip install "partinstall[dataframe]" --upgrade'
    )
    raise ImportError(msg) from e