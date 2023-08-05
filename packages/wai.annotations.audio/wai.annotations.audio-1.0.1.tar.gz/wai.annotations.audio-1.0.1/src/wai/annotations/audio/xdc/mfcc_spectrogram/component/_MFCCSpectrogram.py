import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os

from io import BytesIO

from wai.common.cli.options import TypedOption, FlagOption
from wai.annotations.core.component import ProcessorComponent
from wai.annotations.core.stream import ThenFunction, DoneFunction
from wai.annotations.core.stream.util import RequiresNoFinalisation
from wai.annotations.domain.audio.classification import AudioClassificationInstance
from wai.annotations.domain.image import Image, ImageFormat
from wai.annotations.domain.image.classification import ImageClassificationInstance


class MFCCSpectrogram(
    RequiresNoFinalisation,
    ProcessorComponent[AudioClassificationInstance, ImageClassificationInstance]
):
    """
    Stream processor to generating a plot from Mel-frequency cepstral coefficients.
    """

    num_mfcc: int = TypedOption(
        "--num-mfcc",
        type=int,
        default=20,
        help="the number of MFCCs to return."
    )

    dct_type: int = TypedOption(
        "--dct-type",
        type=int,
        default=2,
        help="the Discrete cosine transform (DCT) type (1|2|3). By default, DCT type-2 is used."
    )

    norm: str = TypedOption(
        "--norm",
        type=str,
        default="ortho",
        help="If dct_type is 2 or 3, setting norm='ortho' uses an ortho-normal DCT basis. Normalization is not supported for dct_type=1. (options: none|ortho)")

    lifter: int = TypedOption(
        "--lifter",
        type=int,
        default=0,
        help="If lifter>0, apply liftering (cepstral filtering) to the MFCC: M[n, :] <- M[n, :] * (1 + sin(pi * (n + 1) / lifter) * lifter / 2)"
    )

    num_fft: int = TypedOption(
        "--num-fft",
        type=int,
        default=2048,
        help="the length of the windowed signal after padding with zeros. should be power of two."
    )

    hop_length: int = TypedOption(
        "--hop-length",
        type=int,
        default=512,
        help="number of audio samples between adjacent STFT columns."
    )

    win_length: int = TypedOption(
        "--win-length",
        type=int,
        default=None,
        help="each frame of audio is windowed by window of length win_length and then padded with zeros to match num_fft. defaults to win_length = num_fft"
    )

    window: str = TypedOption(
        "--window",
        type=str,
        default="hann",
        help="a window function, such as scipy.signal.windows.hann"
    )

    center: bool = FlagOption(
        "--center",
        help="for centering the signal."
    )

    pad_mode: str = TypedOption(
        "--pad-mode",
        type=str,
        default="constant",
        help="used when 'centering'"
    )

    power: float = TypedOption(
        "--power",
        type=float,
        default=2.0,
        help="exponent for the magnitude melspectrogram. e.g., 1 for energy, 2 for power, etc."
    )

    dpi: float = TypedOption(
        "--dpi",
        type=int,
        default=100,
        help="the dots per inch"
    )

    def process_element(
            self,
            element: AudioClassificationInstance,
            then: ThenFunction[ImageClassificationInstance],
            done: DoneFunction
    ):
        data, sample_rate = element.data.audio_data

        # not mono?
        if len(data.shape) > 1:
            data = librosa.to_mono(data)

        # generate spectrogram
        mfccs = librosa.feature.mfcc(y=data, sr=sample_rate, n_mfcc=self.num_mfcc, dct_type=self.dct_type,
                                     norm=(None if (self.norm == "none") else self.norm), lifter=self.lifter,
                                     n_fft=self.num_fft, hop_length=self.hop_length,
                                     win_length=self.win_length, window=self.window, center=self.center,
                                     pad_mode=self.pad_mode, power=self.power)

        # plot
        fig, ax = plt.subplots()
        librosa.display.specshow(mfccs, x_axis='time', y_axis='linear', ax=ax)
        b = BytesIO()
        plt.axis('off')
        plt.savefig(b, format='png', bbox_inches='tight', pad_inches=0, dpi=self.dpi)
        b.seek(0)

        plt.close('all')

        # create output data
        filename_new = os.path.splitext(element.data.filename)[0] + ".png"
        image = Image(filename_new, b.read(), ImageFormat.PNG)
        element_new = ImageClassificationInstance(image, element.annotations)
        then(element_new)
