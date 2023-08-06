from typing import Any, Dict, List, Union

import vapoursynth as vs
from vsutil import join, split

core = vs.core


__all__ = ['Placebo']


class Placebo:
    radius: float
    thrs: List[float]
    iterations: int
    grain: List[float]

    placebodb_args: Dict[str, Any]

    def __init__(self,
                 radius: float = 16.0, threshold: Union[float, List[float]] = 4.0,
                 iterations: int = 1, grain: Union[float, List[float]] = 6.0,
                 **kwargs: Any) -> None:
        """
        Wrapper for placebo.Deband
        https://github.com/Lypheo/vs-placebo#vs-placebo

        :param radius:          The debanding filter's initial radius.
                                The radius increases linearly for each iteration.
                                A higher radius will find more gradients,
                                but a lower radius will smooth more aggressively.

        :param threshold:       The debanding filter's cut-off threshold.
                                Higher numbers increase the debanding strength dramatically,
                                but progressively diminish image details.

        :param iterations:      The number of debanding steps to perform per sample.
                                Each step reduces a bit more banding,
                                but takes time to compute.
                                Note that the strength of each step falls off very quickly,
                                so high numbers (>4) are practically useless.

        :param grain:           Add some extra noise to the image.
                                This significantly helps cover up remaining quantization artifacts.
                                Higher numbers add more noise.
                                Note: When debanding HDR sources, even a small amount of grain can result
                                in a very big change to the brightness level.
                                It's recommended to either scale this value down or disable it entirely for HDR.

        :param kwargs:          Arguments passed to `placebo.Deband`.
        """

        self.radius = radius

        if isinstance(threshold, (float, int)):
            self.threshold = [threshold] * 3
        else:
            self.threshold = threshold + [threshold[-1]] * (3 - len(threshold))

        self.iterations = iterations

        if isinstance(grain, (float, int)):
            self.grain = [grain] * 3
        else:
            self.grain = grain + [grain[-1]] * (3 - len(grain))

        self.placebodb_args = kwargs

    def deband(self, clip: vs.VideoNode) -> vs.VideoNode:
        """
        Main deband function

        :param clip:            Source clip
        :return:                Debanded clip
        """
        if clip.format is None:
            raise ValueError('deband: Variable format not allowed!')

        debs = [
            p.placebo.Deband(1, self.iterations, thr, self.radius, gra, **self.placebodb_args)
            for p, thr, gra in zip(split(clip), self.threshold, self.grain)
        ]
        return debs[0] if len(debs) == 1 else join(debs, clip.format.color_family)
