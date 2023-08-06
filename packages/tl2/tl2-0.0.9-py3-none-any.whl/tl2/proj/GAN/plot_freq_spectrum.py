from tqdm import tqdm

from tl2 import tl2_utils
from tl2.proj.logger import logging_utils_v2
from tl2.proj.argparser import argparser_utils
from tl2.proj.GAN import frequency_spectrum
from tl2.proj.pil import pil_utils


def main(outdir,
         img_dir,
         num_imgs,
         debug,
         ext=('*.jpg', '*.png')
         ):

  logger = logging_utils_v2.get_logger(filename=f"{outdir}/log.txt")

  freq_spec = frequency_spectrum.FrequencySpectrum()

  img_list = tl2_utils.get_filelist_recursive(img_dir, ext=ext)

  if debug:
    num_imgs = 10

  pbar = tqdm(range(num_imgs))
  for idx in pbar:
    img_pil = pil_utils.pil_open_rgb(path=img_list[idx])
    freq_spec.get_spectrum_and_update(image_pil=img_pil)
    if idx % 100 == 0:
      freq_spec_pil = freq_spec.get_spectrum_pil(text=None)
      freq_spec_pil = pil_utils.convert_to_rgb(freq_spec_pil)
      pil_utils.pil_save(freq_spec_pil, f"{outdir}/stylegan2_{idx:03d}_freq_spectrum.png")

  freq_spec_pil = freq_spec.get_spectrum_pil(text=None)
  freq_spec_pil = pil_utils.convert_to_rgb(freq_spec_pil)
  pil_utils.pil_save(freq_spec_pil, f"{outdir}/stylegan2_{num_imgs:03d}_freq_spectrum.png")

  pass


if __name__ == '__main__':
  parser = argparser_utils.get_parser()
  argparser_utils.add_argument_str(parser, name="outdir", )
  argparser_utils.add_argument_str(parser, name="img_dir", )
  argparser_utils.add_argument_int(parser, name="num_imgs", default=100)
  argparser_utils.add_argument_bool(parser, name="debug", )

  args, _ = parser.parse_known_args()

  argparser_utils.print_args(args)


  main(outdir=args.outdir,
       img_dir=args.img_dir,
       num_imgs=args.num_imgs,
       debug=args.debug)
