import cv2
import numpy as np


class FramePreprocessor:
    """
    Automatically improves difficult camera frames.

    Handles:
    - low brightness
    - low contrast
    - uneven lighting
    - mild image noise

    The goal is to improve the input before
    sending it to the pose estimation model.
    """

    def __init__(self):
        self.clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

    def get_brightness(self, frame):
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        return float(
            np.mean(gray)
        )

    def get_contrast(self, frame):
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        return float(
            np.std(gray)
        )

    def gamma_correct(
        self,
        frame,
        gamma
    ):
        if gamma <= 0:
            return frame

        inverse_gamma = 1.0 / gamma

        table = np.array(
            [
                (
                    (i / 255.0)
                    ** inverse_gamma
                ) * 255
                for i in range(256)
            ]
        ).astype("uint8")

        return cv2.LUT(
            frame,
            table
        )

    def improve_contrast(
        self,
        frame
    ):
        lab = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2LAB
        )

        l_channel, a_channel, b_channel = (
            cv2.split(lab)
        )

        l_channel = self.clahe.apply(
            l_channel
        )

        enhanced = cv2.merge(
            [
                l_channel,
                a_channel,
                b_channel
            ]
        )

        return cv2.cvtColor(
            enhanced,
            cv2.COLOR_LAB2BGR
        )

    def denoise(
        self,
        frame
    ):
        return cv2.GaussianBlur(
            frame,
            (3, 3),
            0
        )

    def process(
        self,
        frame
    ):
        """
        Automatically preprocess a camera/video frame.

        The function adapts its processing according
        to the current image conditions.
        """

        if frame is None:
            return None

        result = frame.copy()

        brightness = self.get_brightness(
            result
        )

        contrast = self.get_contrast(
            result
        )

        # -----------------------------------------
        # VERY DARK IMAGE
        # -----------------------------------------

        if brightness < 45:

            result = self.gamma_correct(
                result,
                1.8
            )

        # -----------------------------------------
        # DARK IMAGE
        # -----------------------------------------

        elif brightness < 80:

            result = self.gamma_correct(
                result,
                1.35
            )

        # -----------------------------------------
        # LOW CONTRAST
        # -----------------------------------------

        if contrast < 30:

            result = self.improve_contrast(
                result
            )

        # -----------------------------------------
        # VERY NOISY IMAGE
        # -----------------------------------------

        if contrast < 18:

            result = self.denoise(
                result
            )

        return result


# Shared instance
frame_preprocessor = FramePreprocessor()