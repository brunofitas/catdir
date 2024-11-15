
# **CatDir**

`CatDir` is a command-line tool that lets you traverse and print the contents of a directory, respecting ignore rules defined in a `.catignore` file. It also includes a **reconstruction feature** that allows you to recreate a directory structure from a previously saved output.

## **Features**

- **Traverse and Display**: List and print the contents of files in a directory, similar to `cat`, but over the entire directory structure.
- **Ignore Rules**: Respect patterns specified in a `.catignore` file to exclude certain files from the output.
- **Reconstruction**: Recreate a directory structure from a saved text representation of the directory tree and file contents.
- **Recursive Option**: Optionally traverse directories recursively.

## **Installation**

### Prerequisites

- Python 3.7 or higher

### Install via `pip`

```bash
pip install git+https://github.com/brunofitas/catdir.git
```

### Manual Installation

Clone the repository and install manually:

```bash
git clone https://github.com/brunofitas/catdir.git
cd catdir
pip install .
```

## **Usage**

The `catdir` command has two main modes: **traverse and display** (`catdir`) and **reconstruct** (`catdir --reconstruct`).

### **Basic Usage**

1. Traverse the current directory and display file contents:

```bash
catdir .
```

2. Traverse a specific directory recursively:

```bash
catdir /path/to/dir --recursive true
```

### **Ignoring Files**

Specify patterns to ignore in a `.catignore` file:

**Example `.catignore` file:**

```
*.ignore
*.log
*.tmp
```

This will exclude any files matching these patterns.

### **Saving Output**

You can save the output of `catdir` to a file for later reconstruction:

```bash
catdir . > my_dir_output.txt
```

### **Reconstructing a Directory**

Recreate a directory structure from a previously saved output:

```bash
cat my_dir_output.txt | catdir --reconstruct -
```

This will reconstruct the directory structure and files in the current directory.

## **Example**

### **Directory Structure:**

```bash
test_data/
├── .catignore
├── test.txt
├── ignore.ignore
└── nested/
    ├── nested.txt
    └── ignore.ignore
```

**.catignore:**

```
*.ignore
```

### **Output:**

```bash
$ catdir test_data

####################################################################################################
TREE:
####################################################################################################
test_data/test.txt
test_data/nested/nested.txt
####################################################################################################
# FILES
####################################################################################################
File: test_data/test.txt
Type: text
----------------------------------------------------------------------------------------------------
This is a test file.
====================================================================================================
File: test_data/nested/nested.txt
Type: text
----------------------------------------------------------------------------------------------------
This is a nested file.
====================================================================================================
```

### **Reconstruction:**

Save the output to a file and reconstruct:

```bash
catdir test_data > output.txt
cat output.txt | catdir --reconstruct -
```

This will recreate the `test_data` structure in the current directory.

## **Testing**

Run the unit tests using `unittest`:

```bash
python -m unittest discover tests
```

The test suite covers:
- File ignoring based on `.catignore`.
- Tree creation and rendering.
- Reconstruction of the directory structure.
- End-to-end tests.

## **Contributing**

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Make your changes and commit them: `git commit -m "Add feature"`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Open a pull request.

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## **Contact**

Author: Bruno Fitas  
GitHub: [https://github.com/brunofitas](https://github.com/brunofitas)

