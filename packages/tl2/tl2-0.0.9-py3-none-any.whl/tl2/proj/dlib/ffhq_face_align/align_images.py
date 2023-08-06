from pathlib import Path
import argparse
import os
import sys
import bz2
import tqdm
# from tensorflow.keras.utils import get_file

from tl2.proj.dlib.ffhq_face_align.face_alignment import image_align
from tl2.proj.dlib.ffhq_face_align.landmarks_detector import LandmarksDetector


def unpack_bz2(src_path, dst_path):
    data = bz2.BZ2File(src_path).read()
    with open(dst_path, 'wb') as fp:
      fp.write(data)
    print(f"Unzip {src_path} to \n{dst_path}")
    return dst_path


def get_saved_align_image_path(outdir, image_path, idx):
    image_path = Path(image_path)
    if outdir is None:
        saved_image = f"{image_path.parent}/{image_path.stem}_aligned_{idx:02d}.png"
    else:
        saved_image = f"{outdir}/{image_path.stem}_aligned_{idx:02d}.png"
    return saved_image


def align_face(image_path,
               outdir=None,
               output_size=1024,
               landmark_model="cache_pretrained/dlib/shape_predictor_68_face_landmarks.dat",
               landmark_model_bz2="cache_pretrained/dlib/shape_predictor_68_face_landmarks.dat.bz2"):
    """
    Extracts and aligns all faces from images using DLib and a function from original FFHQ dataset preparation step

    """
    os.makedirs(outdir, exist_ok=True)

    LANDMARKS_MODEL_URL = 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'
    # tmp = get_file(landmark_model, LANDMARKS_MODEL_URL)
    if not os.path.exists(landmark_model):
      landmark_model = unpack_bz2(src_path=landmark_model_bz2, dst_path=landmark_model)

    landmarks_detector = LandmarksDetector(landmark_model)

    image_path = Path(image_path)
    landmarks = landmarks_detector.get_landmarks(str(image_path))
    saved_image_list = []
    det_success = False
    for i, face_landmarks in enumerate(landmarks):
        saved_image = get_saved_align_image_path(outdir=outdir, image_path=image_path, idx=i)
        saved_image_list.append(saved_image)
        image_align(image_path, saved_image, face_landmarks, output_size=output_size)
        det_success = True
        pass

    if not det_success:
        tqdm.tqdm.write(f"Fail to align: {image_path}")
    return saved_image_list


if __name__ == '__main__':
    """
    python -m tl2.proj.dlib.ffhq_face_align.align_images --image_path --outdir
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--landmark_model', type=str,
                        default="datasets/pretrained/shape_predictor_68_face_landmarks.dat.bz2")
    parser.add_argument('--image_path', type=str)
    parser.add_argument('--outdir', type=str)

    args, _ = parser.parse_known_args()

    align_face(**vars(args))






