from argparse import ArgumentParser
import re
from pathlib import Path
import csv
import os
import yaml

parser = ArgumentParser()
parser.add_argument(
    "-i",
    "--input",
    type = str,
    required=True,
    help = "CSV file to parse"
)
parser.add_argument(
    "-t",
    "--target",
    type = str,
    required=True,
    help = "Path to the target OSS-Fuzz repo",
)
parser.add_argument(
    "-o",
    "--output",
    type = str,
    required=True,
    help = "Output file to store results"
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help = "Enable verbose mode"
)
args = parser.parse_args()

OSS_FUZZ_PATH = Path(args.target)
PROJECTS_DIR = OSS_FUZZ_PATH / "projects"
REGEX = re.compile("(https?://)?(www.)?github.com/(\\w+)/(\\w+)(.git)?/?")


def is_same_url(lhs: str, rhs: str) -> bool:
    lhs_match = REGEX.match(lhs)
    rhs_match = REGEX.match(rhs)
    if not lhs_match or not rhs_match:
        return False

    author_pos = 3
    repo_pos = 4

    lhs_author = lhs_match.group(author_pos).lower() if lhs_match.group(author_pos) else None
    lhs_repo = lhs_match.group(repo_pos).lower() if lhs_match.group(repo_pos) else None

    rhs_author = rhs_match.group(author_pos).lower() if rhs_match.group(author_pos) else None
    rhs_repo = rhs_match.group(repo_pos).lower() if rhs_match.group(repo_pos) else None

    return lhs_author == rhs_author and lhs_repo == rhs_repo


def get_url_from_config(yaml_path: Path) -> str:
    if not yaml_path.exists():
        return ""

    main_repo_url = ""
    with open(yaml_path) as f:
        config = yaml.safe_load(f)
        main_repo_url = config.get("main_repo", "")

    return main_repo_url


def cache_integrated_projects() -> dict[str, str]:
    cache = {}
    projects = [f.name for f in os.scandir(PROJECTS_DIR) if f.is_dir()]

    for project in projects:
        yaml_path = PROJECTS_DIR / project / "project.yaml"
        if url := get_url_from_config(yaml_path):
            cache[project] = url

    return cache


def short_circuit_check(cached_projects: dict[str, str], repo_url: str) -> bool:
    repo_name = repo_url[repo_url.rstrip("/").rfind("/") + 1:]
    return is_same_url(repo_url, cached_projects.get(repo_name, ""))


def brute_force_check(cached_projects: dict[str, str], repo_url: str) -> bool:
    for cached_url in cached_projects.values():
        if is_same_url(repo_url, cached_url):
            return True

    return False


def check_fuzz_integration(cached_projects: dict[str, str], repo_url: str) -> bool:
    return short_circuit_check(cached_projects, repo_url) or brute_force_check(cached_projects, repo_url)


def main():
    sortedlist = []
    with open(args.input, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        sortedlist = sorted(reader, key=lambda row:(row["default_score"]), reverse=True)

    cached_projects = cache_integrated_projects()
    with open(args.output, "w") as f:
        for row in sortedlist:
            repo_url = row["repo.url"]
            if not check_fuzz_integration(cached_projects, repo_url):
                output = f"[OPPORTUNITY]: {repo_url}"
                print(output)
                f.write(output + "\n")
            elif args.verbose:
                print(f"[INTEGRATED]: {repo_url}")


if __name__ == "__main__":
    main()

