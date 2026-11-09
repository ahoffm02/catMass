"""`python -m catmass` starts the app (same as the `catmass` command)."""
from catmass.app import main

if __name__ in {'__main__', '__mp_main__'}:
    main()
