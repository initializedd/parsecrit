# parsecrit

parsecrit aims to automate the process of discovering open source libraries that have not been integrated as an [OSS-Fuzz](https://github.com/google/oss-fuzz) project, enabling contributors to spend less time searching for an integration opportunity. It does this by checking whether any of the integrated [OSS-Fuzz](https://github.com/google/oss-fuzz) projects have defined a GitHub URL in their `project.yaml` file that matches another within the [criticality_score](https://github.com/ossf/criticality_score) CSV file given as input to the script.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 parsecrit.py --input <input> --target <target> --output <output>
```

where:

- `<input>` is the path to a [criticality_score](https://github.com/ossf/criticality_score) CSV file on disk; and
- `<target>` is the path to the up-to-date [OSS-Fuzz](https://github.com/google/oss-fuzz) repo on disk; and
- `<output>` is the path where the results should be saved on disk.

