import numpy as np
from scipy.ndimage import rotate
import cv2


class ImageProcessor:
    def __init__(self, img_path: str) -> None:
        self.img = cv2.imread(img_path)

    def enhance_image(
        self, high_contrast: bool = True, gaussian_blur: bool = True, show: bool = False
    ) -> np.ndarray:
        self.img = self.rescale_image()

        self.img = self.deskew_image()
        self.img = self.remove_shadows()

        if high_contrast:
            self.img = self.grayscale_image()

        if gaussian_blur:
            self.img = self.remove_noise()

        if show:
            self.show_image()

        return self.img

    def deskew_image(self, delta: float = 0.2, limit: float = 1) -> np.ndarray:
        def determine_score(arr, angle):
            data = rotate(arr, angle, reshape=False, order=0)
            histogram = np.sum(data, axis=1)
            score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
            return histogram, score

        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        scores = []
        angles = np.arange(-limit, limit + delta, delta)
        for angle in angles:
            _, score = determine_score(thresh, angle)
            scores.append(score)

        best_angle = angles[scores.index(max(scores))]

        (h, w) = self.img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, best_angle, 1.0)

        rotated = cv2.warpAffine(
            self.img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )

        return rotated

    def remove_shadows(self) -> np.ndarray:
        rgb_planes = cv2.split(self.img)

        result_planes = []
        result_norm_planes = []
        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(
                diff_img,
                None,
                alpha=0,
                beta=255,
                norm_type=cv2.NORM_MINMAX,
                dtype=cv2.CV_8UC1,
            )
            result_planes.append(diff_img)
            result_norm_planes.append(norm_img)

        result = cv2.merge(result_planes)

        return result

    def rescale_image(self) -> np.ndarray:
        self.img = cv2.resize(
            self.img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC
        )
        return self.img

    def grayscale_image(self) -> np.ndarray:
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        return self.img

    def remove_noise(self) -> np.ndarray:
        kernel = np.ones((1, 1), np.uint8)
        self.img = cv2.dilate(self.img, kernel, iterations=1)
        self.img = cv2.erode(self.img, kernel, iterations=1)

        self.img = cv2.threshold(
            cv2.GaussianBlur(self.img, (5, 5), 0),
            150,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]
        self.img = cv2.threshold(
            cv2.bilateralFilter(self.img, 5, 75, 75),
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]
        self.img = cv2.adaptiveThreshold(
            cv2.bilateralFilter(self.img, 9, 75, 75),
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            2,
        )

        return self.img

    def show_image(self) -> None:
        # Display the thresholded image
        # Create a resizable window
        cv2.namedWindow("Thresholded Image", cv2.WINDOW_NORMAL)

        # Resize the window to 800x600
        cv2.resizeWindow("Thresholded Image", 800, 600)

        # Display the thresholded image
        cv2.imshow("Thresholded Image", self.img)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
