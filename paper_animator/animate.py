import typing
import numpy as np
from pathlib import Path
from tqdm import tqdm

from skvideo.io import FFmpegWriter
import png

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.image as mpimg


def animate_images(figures:typing.List[np.ndarray], out_file:Path, frame_dur=1, fps:int=30):
    out_file = Path(out_file).with_suffix('.mp4')

    writer = FFmpegWriter(out_file, inputdict={'-r':str(fps)})

    print(f'\nWriting frames to {out_file}')

    for fig in tqdm(figures):
        for frame in range(round(frame_dur*fps)):
            writer.writeFrame(fig)

    writer.close()

    print('\nWriting complete!')

def save_figs(figs, output_dir):
    output_dir = Path(output_dir)
    for i, fig in enumerate(figs):
        png.from_array(np.reshape(fig, (-1, fig.shape[1]*3)), mode="RGB").save(str(output_dir / f"{i:03}.png"))




def plot_img_dirs(img_dir:Path, resolution=(1920,1080), shape=None):
    img_dir = Path(img_dir)

    # find max number of images
    if img_dir.name != 'img':
        if (img_dir / 'img').exists():
            img_dir = img_dir / 'img'
        else:
            # give it a shot i guess
            pass

    # iterate through folders, finding max images
    if shape is None:
        subdirs = sorted([subdir for subdir in img_dir.iterdir() if subdir.is_dir()])
        max_images = 0
        for subdir in subdirs:
            img_files = [img_file for img_file in subdir.iterdir() if img_file.suffix == '.png']
            n_images = len(img_files)
            if n_images > max_images:
                max_images = n_images

        cols = np.ceil(np.sqrt(max_images*resolution[0]/resolution[1])).astype(int)
        rows = np.ceil(max_images / cols).astype(int)
    else:
        rows, cols = shape

    # convert px to inches for matplotlib
    resolution_in = (resolution[0]/plt.rcParams['figure.dpi'], resolution[1]/plt.rcParams['figure.dpi'])


    fig, ax = plt.subplots(ncols=cols, nrows=rows, figsize=resolution_in,
                           tight_layout = True)

    for an_ax in ax.flatten():
        an_ax.axis('off')

    # iterate through image directories
    print('\nRendering image frames')
    figures = []
    for subdir in tqdm(subdirs, position=0):
        img_files = sorted([img_file for img_file in subdir.iterdir() if img_file.suffix == '.png'])
        if len(img_files) == 0:
            continue
        for i, img_file in enumerate(img_files):
            img = mpimg.imread(img_file)
            ax[np.floor(i/cols).astype(int), int(i%cols)].imshow(img)

        for an_ax in ax.flatten():
            an_ax.axis('off')

        plt.pause(0.01)

        # get figure as array
        fig_arr = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        fig_arr = fig_arr.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        figures.append(fig_arr)

        # clear axes
        for an_ax in ax.flatten():
            an_ax.cla()

    plt.close(fig)
    return figures



    # iterate through


