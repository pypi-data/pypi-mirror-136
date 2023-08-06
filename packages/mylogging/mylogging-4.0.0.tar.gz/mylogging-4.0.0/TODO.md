Change config so it uses Literal instead of options and annotations instead of type in check
Fix filter error so it stops also on warnings

Reformat warnings functions to module warnings

Make around not automatic, but only for to_file = False
Add caption default to none and if not to file, then use default

Allow file rotations

Add .ipynb example - add this to `pyproject.toml`
    
    python_files = ["test*.py", "demo.ipynb"]
