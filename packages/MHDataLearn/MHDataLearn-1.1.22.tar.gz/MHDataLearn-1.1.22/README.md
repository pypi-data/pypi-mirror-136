# MHDataLearn

MHDataLearn is a Python package, with functions to enable classification machine learning models to be applied and evaluated to a Mental Health Services Data Set (MHSDS).

The package includes:
- preprocessing tools to clean and convert raw MHSDS data in to a format suitable for machine learning algorithms
- tools for splitting test and training data and training multiple classification algorithms
- visualisation of algorithm performance metrics and confusion matrices to evaluate the best performing module
- in future releases, tools to facilitate use of the trained models on new (unseen) data will be implemented

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install MHDataLearn.

```bash
pip install MHDataLearn
```

## Usage

Below is an example usage of MHDataLearn. It uses a default MHSDS dataset (DummyData.csv) which is included in the package. The functions clean and preprocess the data, then train classification algorithms to predict patient emergency readmissions within 30 days of discharge from features within the dataset. Finally, model performance metrics are visualised.

```python
import MHDataLearn
from MHDataLearn.preprocessing import load, process
from MHDataLearn.modelselector.default_models import train_default_models

# load the default MHSDS dataset
df = load.load_data()

# preprocess the data in preparation for ml models
df = process.wrangle_data(df)

# split data in to test/train, train models and report performance metrics
models = train_default_models(df)
```

The functions in this usage example are high-level functions which combine multiple functions within the MHDataLearn package for ease of use. However, it is expected that users may wish to utilise individual functions for specific preprocessing or machine learning tasks. As an example, here is how a user would utilise the function 'check_emergency' to add a flag to emergency admissions from a raw MHSDS dataset.

```python
import MHDataLearn
from MHDataLearn.preprocessing import load, calculate

# load the default MHSDS dataset
df = load.load_data()

# flag emergency admissions
df = calculate.check_emergency(df)
```
More detailed instructions on usage are provided in the 'User Guide' which comes with the package.

## Contributing
We would welcome your input! We would encourage users to:
- Report a bug
- Discuss the current state of the code
- Submit a fix
- Propose new features
- Become a maintainer

### Contribution environment
To contribute in the development of this package use the environment.yml file to create a similar 
working conda environment.
```
conda create --name -f environment.yml
```
### We develop with GitHub

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests. Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.

We use GitHub issues to track public bugs. Report a bug by opening a new issue.

### Contribution licences
Any contributions will be under the MIT licence.

## License
[MIT](https://choosealicense.com/licenses/mit/)

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.