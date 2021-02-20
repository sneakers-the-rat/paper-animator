VERSION = "0.0.1"

import argparse
from pathlib import Path
import shutil
from paper_animator import animate, extract

def parse_args():
    parser = argparse.ArgumentParser(description="Convert a version controlled paper to a video!")
    parser.add_argument('input', type=str, help="Input file, a .pdf or .tex file!", default=None)
    parser.add_argument('--output', type=str, help="Output video file, if absent, input with .mp4 extension, default: %(default)s",required=False)
    parser.add_argument('--repo', type=str, help="URL to a git repository to clone, if absent, get repo from input file, default: %(default)s", default=None,required=False)
    parser.add_argument('--branch', type=str, help="Which branch to use, default: %(default)s", default='main',required=False)
    parser.add_argument('--tmp_dir', type=str, help="Temporary directory to use, otherwise create one in ~/, default: %(default)s", default=None,required=False)
    parser.add_argument('--latex_builder', help="if input is a latex file, which builder to use with latexmk, default: %(default)s", choices=['pdflatex', 'xetex'],required=False, default='pdflatex')
    parser.add_argument('--frame_duration', type=float, help="Duration (in s) to show each commit, default: %(default)s", default=1,required=False)
    parser.add_argument('--video_fps', type=int, help="fps of output video, default: %(default)s", default=30,required=False)
    parser.add_argument('--resolution', type=tuple, help="Resolution of plots, default: %(default)s", default=(1920,1080),required=False)
    parser.add_argument('--grid_shape', type=tuple, help="Manually override (rows,cols) of figure layout, default: %(default)s", default=None,required=False)
    parser.add_argument('--dont_cleanup', action="store_true", help="Delete temporary folder after completion")

    return parser.parse_args()



def main():
    args = parse_args()

    input_file = Path(args.input)


    if args.output is None:
        output_file = input_file.with_suffix('.mp4')
    else:
        output_file = Path(args.output)


    temp_dir = extract.extract_images(input_file, repo=args.repo, branch=args.branch,
                                     out_dir=args.tmp_dir, builder=args.latex_builder)
    figs = animate.plot_img_dirs(temp_dir/'img', resolution=args.resolution, shape=args.grid_shape)
    animate.animate_images(figs, out_file=output_file, frame_dur=args.frame_duration, fps=args.video_fps)

    if args.dont_cleanup:
        print(f"Temporary files left in {temp_dir}")
        # write out the figs, they may want them
        fig_dir = temp_dir / 'figs'
        fig_dir.mkdir(exist_ok=True)
        animate.save_figs(figs, fig_dir)

    else:
        print(f'Removing temporary files in {temp_dir}')
        shutil.rmtree(temp_dir)



# if __name__ == "__main__":
#
#     main()


