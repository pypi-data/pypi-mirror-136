from io import BytesIO
import multiprocessing
import sys
from time import time
import pdf2image
import numpy as np
from .engine import get_instruments_dict, predict_parts, TesserocrDetections
from PyPDF2 import PdfFileReader
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PSM, OEM


class SimpleTimer:
    def __init__(self):
        self.time = time()
    
    def __str__(self):
        return str(time() - self.time)


class PdfPredictor():
    def __init__(
        self,
        pdf : BytesIO | bytes,
        instruments=None,
        instruments_file=None,
        instruments_file_format="yaml",
        use_lstm=False,
        tessdata_dir=None,
        log_stream=sys.stdout,
        crop_to_top=False,
        crop_to_left=True,
        ):
        self.instruments = get_instruments_dict(
            instruments=instruments,
            instruments_file=instruments_file,
            instruments_file_format=instruments_file_format,
        )
        self.pdf = pdf
        if type(self.pdf) == BytesIO:
            self.pdf = self.pdf.getvalue()
        self.use_lstm = use_lstm
        self.tessdata_dir = tessdata_dir
        self.log_stream = log_stream
        self.crop_to_top = crop_to_top
        self.crop_to_left = crop_to_left
        self.crop = crop_to_top or crop_to_left
    
    def log(self, *msg):
        if self.log_stream is None:
            return
        print(*msg, file=self.log_stream)

    def parts(self):
        lastPartName = ""
        lastPartNumber = 0
        lastPartNamePage = 0
        lastInstruments = []
        pdfReader = PdfFileReader(BytesIO(self.pdf))
        for i in range(pdfReader.getNumPages()):
            self.log("page", i+1, "of", pdfReader.getNumPages())
            img = pdf2image.convert_from_bytes(self.pdf, dpi=200, first_page=i+1, last_page=i+1)[0]
            if self.crop:
                self.log("cropping...")
                if self.crop_to_top:
                    img = img.crop((0, 0, img.width, img.height//2))
                if self.crop_to_left:
                    img = img.crop((0, 0, img.width//2, img.height))
            self.log("detecting...")
            timer = SimpleTimer()
            tesserocr_kwargs = {
                "psm": PSM.SPARSE_TEXT,
            }
            if self.use_lstm:
                tesserocr_kwargs["oem"] = OEM.LSTM_ONLY
            if self.tessdata_dir != None:
                tesserocr_kwargs["path"] = self.tessdata_dir
            with PyTessBaseAPI(**tesserocr_kwargs) as api:
                api.SetImage(img)
                api.Recognize()
                self.log(f"done in {timer} seconds")
                self.log("predicting...")
                timer = SimpleTimer()
                detections = TesserocrDetections(api)
                parts = list(predict_parts(detections, self.instruments))
                self.log(f"done in {timer} seconds")
                self.log("parts:", [part for part in parts])
                for j, (name, part_number, instruments) in enumerate(parts):
                    if lastPartName == name:
                        continue
                    if lastPartName:
                        yield {
                            "name": lastPartName,
                            "partNumber": lastPartNumber,
                            "instruments": lastInstruments,
                            "fromPage": lastPartNamePage,
                            "toPage": i if j == 0 else i+1
                        }
                    lastPartName = name
                    lastPartNumber = part_number
                    lastPartNamePage = i+1
                    lastInstruments = instruments
        if lastPartName:
            yield {
                "name": lastPartName,
                "partNumber": lastPartNumber,
                "instruments": lastInstruments,
                "fromPage": lastPartNamePage,
                "toPage": pdfReader.getNumPages()
            }
