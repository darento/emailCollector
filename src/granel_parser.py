import numpy as np
import re
import pytesseract
import cv2
from scipy.ndimage import rotate

from src.utils import convert_to_float
from src.ticket_parser import AbstractTicketParser


class GranelTicketParser(AbstractTicketParser):
    def _parse_date_from_file_path(self) -> str:
        # Extract the date from the file name
        # The date is the first 8 characters of the file name
        # The format is YYYYMMDD
        return self.file_path.split("/")[-1][:8]

    def _clean_ocr_text(self, text: str) -> str:
        # Remove unwanted characters
        text = re.sub(r"[|]", "", text)

        # Replace multiple occurrences of newlines with a single newline
        text = re.sub(r"\n+", "\n", text)

        # Remove spaces after dots and commas (for price and weight parsing)
        text = re.sub(r"(?<=\.) +(?=\d)|(?<=\d) +(?=,)", "", text)

        return text

    def _parse_ticket(self) -> None:
        # Extract the text from the JPEG
        img = cv2.imread(self.file_path)
        img_prepared = self._enhance_image(img, show=True)
        text = pytesseract.image_to_string(
            img_prepared, lang="cat+eng+spa", config="--psm 4 --oem 1"
        )
        cleaned_text = self._clean_ocr_text(text)
        print(cleaned_text)
        return cleaned_text

    def _deskew_image(self, image, delta=0.2, limit=1):
        def determine_score(arr, angle):
            data = rotate(arr, angle, reshape=False, order=0)
            histogram = np.sum(data, axis=1)
            score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
            return histogram, score

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        scores = []
        angles = np.arange(-limit, limit + delta, delta)
        for angle in angles:
            histogram, score = determine_score(thresh, angle)
            scores.append(score)

        best_angle = angles[scores.index(max(scores))]

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, best_angle, 1.0)

        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )

        return rotated

    def _remove_shadows(self, img):
        rgb_planes = cv2.split(img)

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

    def _rescale_image(self, img):
        img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
        return img

    def _grayscale_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def _remove_noise(self, img):
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)

        img = cv2.threshold(
            cv2.GaussianBlur(img, (5, 5), 0),
            150,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]
        img = cv2.threshold(
            cv2.bilateralFilter(img, 5, 75, 75),
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]
        img = cv2.adaptiveThreshold(
            cv2.bilateralFilter(img, 9, 75, 75),
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            2,
        )

        return img

    def _enhance_image(self, img, high_contrast=True, gaussian_blur=True, show=False):
        img = self._rescale_image(img)

        img = self._deskew_image(img)
        img = self._remove_shadows(img)

        if high_contrast:
            img = self._grayscale_image(img)

        if gaussian_blur:
            img = self._remove_noise(img)

        if show:
            self._show_image(img)

        return img

    def _show_image(self, img):
        # Display the thresholded image
        # Create a resizable window
        cv2.namedWindow("Thresholded Image", cv2.WINDOW_NORMAL)

        # Resize the window to 800x600
        cv2.resizeWindow("Thresholded Image", 800, 600)

        # Display the thresholded image
        cv2.imshow("Thresholded Image", img)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def parse_line(self, lines_iter):
        for line in lines_iter:
            product = " ".join(line.strip().split(" ")[1:])
            next_line = next(lines_iter)
            next_line_split = next_line.strip().split(" ")
            weight_kg = convert_to_float(next_line_split[0])
            price_per_kg = convert_to_float(next_line_split[1])
            total_price = convert_to_float(next_line_split[2])
            item = {
                "product": product,
                "weight_kg": weight_kg,
                "price_per_kg": price_per_kg,
                "total_price": total_price,
            }
            yield item

    def extract_items(self):
        # Find the start and end of the items
        start = self.text.find("ART")
        end = self.text.find("TOTAL")
        items_text = self.text[start:end]

        # remove first and last line (Descripción and empty line)
        lines = items_text.split("\n")[1:-1]

        self.logger.debug(f"TEXT: \n{self.text}")
        self.logger.debug(f"LINES: \n{lines}")

        # create iterator to check next line
        lines_iter = iter(lines)

        for item in self.parse_line(lines_iter):
            self.items.append(item)
        self.logger.debug(f"Extracted items: {self.items}")
        return self.items

    def calculate_total_price(self):
        self.total_price = sum(item["total_price"] for item in self.items)
        if self.total_price == 0:
            self.logger.warning("Total price is 0. Check the parser!")
        return self.total_price
