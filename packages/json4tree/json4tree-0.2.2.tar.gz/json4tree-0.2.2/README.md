# json4tree
Makes any JSON compatible with [D3's hierarchy or tree chart formats](https://d3js.org).

## Installation
Since this tool is exclusively `Python3`, you'll need `pip3` to install:
```
pip3 install json4tree
```
You can also download and install the package directly from [PyPi](https://pypi.org/project/json4tree/0.1.5/).
## Usage
If your `Python3` library is included in your path, try running `json4tree` directly from the command line:
_Note: The long name is a workaround until a bug with the `__main__` script is fixed_
```bash
python3 json4tree/__init__.py input.json output.json
```
Otherwise, you can import it as a module in your `Python3` script:
```python
# import the necessary modules
import json
import json4tree from json4tree

# import your JSON data
infile = open("input.json", "r")
json_file = json.load(infile)
infile.close()

# create a new handler
handler = json4tree(json_file)

# You can either print your results...
handler.results

# Or you can save your results
outfile = open("output.json", "w")
outfile.write(handler.results)
outfile.close()
```
## Examples
Here is an example [input file](https://github.com/robertjamison/json4tree/sample/input.json) from [Merriam-Webster's Dictionary API](https://www.dictionaryapi.com/products/json) and the resulting [output file](https://github.com/robertjamison/json4tree/sample/output.json).
