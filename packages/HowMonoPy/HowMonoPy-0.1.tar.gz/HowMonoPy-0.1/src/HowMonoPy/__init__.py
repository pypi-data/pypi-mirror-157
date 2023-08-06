try:
    from HowMonoPy._wrapper import Analyser
except FileNotFoundError:
    raise ImportError("OS not supported")
