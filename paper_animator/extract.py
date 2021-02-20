import typing
import os
import subprocess
from git import Repo
from pathlib import Path
import fitz
from tqdm import tqdm

# requirements
# gitpython

def find_repo_root(filename: str) -> Path:
    repodir = os.popen(f'git -C {filename} rev-parse --show-toplevel').read().rstrip('\n')
    return Path(repodir)

def extract_images(tex_file, branch=0, out_dir:typing.Optional[str]=None, builder='xelatex'):

    # tex directory
    tex_dir = Path(tex_file).parent
    tex_file = Path(tex_file)
    pdf_file = tex_file.with_suffix('.pdf')

    if out_dir is None:
        out_dir = Path.cwd()
    else:
        out_dir = Path(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    # get repo root
    repo_root = find_repo_root(tex_file)

    # TODO: check if need to clone
    # Repo.clone_from(url, path)

    repo = Repo(repo_root)

    # select branch
    branch = repo.heads[branch]

    # iterate through commits
    commits = list(reversed(list(repo.iter_commits(branch))))
    for i, commit in enumerate(tqdm(commits, total=len(commits), position=0)):
        repo.git.stash()
        repo.git.checkout(commit)

        result = subprocess.run(f'latexmk -{builder} {tex_file.name}', shell=True, cwd=tex_dir,
                                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        if result.returncode == 0:

            # make subdir
            subdir = out_dir / f"{i:03}_{commit.hexsha}"
            subdir.mkdir(exist_ok=True)

            doc = fitz.open(pdf_file)
            for j, page in enumerate(tqdm(doc.pages(), position=1)):
                pix = page.getPixmap(matrix=fitz.Matrix(2,2))
                pix.writeImage((subdir / f"{page.number:04}.png").__str__())


        else:
            print(f'something wrong with build in commit {commit.hexsha}!')









def animate_paper_repo(repo_url, repo_dir = None):

    if repo_dir is None:
        #  
        pass
