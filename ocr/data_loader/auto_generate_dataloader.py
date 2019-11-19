import os

import numpy as np

from ocr.data_loader.vocab import Vocab
from trdg.generators import GeneratorFromWikipedia
from ocr.data_loader.collate import collate_wrapper
from ocr.data_loader.data_loaders import OCRDataLoader


class AutoGenerateDataloader:
    def __init__(self, data_dir, batch_size, **kwargs):
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.kwargs = kwargs

        self.voc = Vocab()
        self.voc.build_vocab_from_char_dict_file(self.get_data_path('vocab.json'))

        self.generator = GeneratorFromWikipedia(count=-1, size=64, language='ja',
                                                skewing_angle=2, random_skew=True, blur=1, random_blur=True,
                                                background_type=3, distorsion_type=-1)

    def __iter__(self):
        return self

    def __next__(self):
        """
        We need to generate a batch of data here
        :return:
        """
        data = []

        for _ in range(self.batch_size):
            image, label = next(self.generator)
            label = self.voc.get_indices_from_label(label)
            data.append({"image": np.array(image), "label": label})

        return collate_wrapper(data)

    def __len__(self):
        return 1

    def split_validation(self):
        """
        Should we use real data for validation test?
        :return:
        """
        val_dataloader = OCRDataLoader(data_dir='../data/real/printed',
                                       json_path='printed.json',
                                       batch_size=self.batch_size,
                                       training=False,
                                       shuffle=False,
                                       num_workers=4,
                                       collate_fn=collate_wrapper)

        return val_dataloader

    def get_vocab(self):
        return self.voc

    def get_data_path(self, path):
        return os.path.join(self.data_dir, path)


if __name__ == '__main__':
    import cv2

    generator = GeneratorFromWikipedia(count=-1, size=64, language='ja',
                                       skewing_angle=2, random_skew=True, blur=1, random_blur=True,
                                       background_type=3, distorsion_type=-1)

    for i, (img, lbl) in enumerate(generator):
        cv2.imwrite('../data/generated/' + str(i) + '.png', img)
