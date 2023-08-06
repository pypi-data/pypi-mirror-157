# Andor SIF

This package has been merged with [fujiisoup/sif_parser](https://github.com/fujiisoup/sif_parser)
and will no longer be mainted.

---

Parse `.sif` files from an Andor spectrometer.

> Install with `python -m pip install andor-sif`

## Parser
The `andor_sif.parse(<file>)` method is used to parse a .sif file.
This is the main function of this package.

## CLI
Installs a command line interface (CLI) named `andor_sif` that can be used to
convert .sif files to .csv.

## Example

### Library
```python
import pandas as pd
import andor_sif as sif


# parse the 'my_pl.sif' file
(data, info) = sif.parse('my_pl.sif')

# place data into a pandas Series
df = pd.Series(data[:, 1], index = data[:, 0])
```

### CLI
Convert all .sif files in the current directory to .csv.
```bash
andor_sif
```

Convert all .sif files ending in `pl` in the current directly into a single .csv.
```bash
andor_sif --join *pl.sif
```

# Parsing `.sif` files
This package uses [`@fujiisoup/sif_reader`](https://github.com/fujiisoup/sif_reader) to parse `.sif` files.
