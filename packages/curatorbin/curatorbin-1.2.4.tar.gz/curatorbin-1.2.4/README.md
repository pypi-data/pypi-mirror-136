Downloads [curator](https://github.com/mongodb/curator) as package data. 

## Usage

The wheel file is a bit beefy, but curator can now be used as such:

```python
import curatorbin

curatorbin.run_curator(first_curator_arg, second_curator_arg)

```
Alternatively, you can get the path with `get_curator_path`.

## Building the package:

You can use `./update_from_curator.sh <major|minor|patch>` for this.

For example, `./update_from_curator.sh minor` will update the minor version, which would turn `1.2.3` to `1.3.0` in setup.py.

After running `update_from_curator.sh`, commit and run a mainline or patch build.
Make sure to use the `publish-to-testpypi` evergreen task.
This will only finish successfully once.
Subsequent runs will fail unless you also increment the version.

#### Note on placeholder.txt

The `placeholder.txt` files do not need to be updated, as the `get-bins` function in the evergreen yaml will get the bins automatically.
However, these are required to make sure that the necessary directories are in git, which helps with distribution.
