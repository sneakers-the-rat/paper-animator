import typing
import os
import subprocess
import shutil
from datetime import datetime
from git import Repo
from pathlib import Path
import fitz
from tqdm import tqdm

# requirements
# gitpython

def find_repo_root(filename: Path) -> Path:
    if filename.is_file():
        filename = filename.parent
    repodir = os.popen(f'git -C {filename} rev-parse --show-toplevel').read().rstrip('\n')
    return Path(repodir)

def extract_images(target_file:Path, repo=None, branch=0, out_dir:typing.Optional[str]=None, builder='xelatex') -> Path:
    # TODO: if given a .pdf file, just look for pdf file each time


    # make a temporary output dir
    if not out_dir:
        out_dir = Path().home() / f'.tmp-paper-animator-{datetime.now().strftime("%y%m%d-%H%M%S")}'
        out_dir.mkdir()
    else:
        out_dir = Path(out_dir)

    repo_dir = out_dir / 'repo'
    img_dir = out_dir / 'img'
    img_dir.mkdir(exist_ok=True)

    if repo_dir.exists():
        shutil.rmtree(repo_dir)

    # clone the repo inside the temporary dir so we don't fuck up the local repo if we got one
    if repo is None:
        # use local repo that the file is in, assume we got an absolute path
        repo_root = find_repo_root(target_file)

        repo = Repo(repo_root).clone(repo_dir)
        # make target file relative to new repo dir
        target_file = repo_dir / target_file.relative_to(repo_root)

    else:
        # assume we got a github url
        repo = Repo.clone_from(repo, to_path=repo_dir)

        # target file should be relative to repo root
        target_file = repo_dir / target_file

    print(f'\nRepository cloned to {repo_dir}')

    # if given a .tex file, build .tex file
    # if given a .tex file, build .tex file
    target_file = Path(target_file)
    if target_file.suffix == '.pdf':
        mode = 'pdf'
        tex_file = None
        tex_dir = None
        pdf_file = target_file

    elif target_file.suffix == '.tex':
        mode = 'tex'
        tex_file = target_file
        tex_dir = target_file.parent
        pdf_file = target_file.with_suffix('.pdf')
    else:
        raise ValueError(f'Dont know how to extract from {target_file}')

    # extract images

    # select branch
    branch = repo.heads[branch]

    commits = list(reversed(list(repo.iter_commits(branch))))
    print('Extracting images from commits')
    for i, commit in enumerate(tqdm(commits, total=len(commits))):
        repo.git.checkout(commit)

        if mode == "tex":
            result = subprocess.run(f'latexmk -{builder} {tex_file.name}', shell=True, cwd=tex_dir,
                                    stdout=subprocess.DEVNULL)

            if result.returncode == 0:
                continue

            else:
                print(f'something wrong with build in commit {commit.hexsha}!')

        # make subdir for commit
        subdir = img_dir / f"{i:03}_{commit.hexsha}"
        subdir.mkdir(exist_ok=True)

        if not pdf_file.exists():
            print(f'file doesnt exist in commit {i} - {commit}')
            continue

        doc = fitz.open(pdf_file)
        for j, page in enumerate(doc.pages()):
            pix = page.getPixmap(matrix=fitz.Matrix(2, 2))
            pix.writeImage((subdir / f"{page.number:04}.png").__str__())

    return out_dir


