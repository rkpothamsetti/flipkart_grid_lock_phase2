import unittest
from PIL import Image
import os
import sys

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.enhancement import check_image_degradation, enhance_image
from pipeline.detector import detect_objects
from pipeline.rules import check_violations
from pipeline.ocr import recognize_plate, validate_plate_format

class TestPipeline(unittest.TestCase):
    
    def test_low_light_detection(self):
        # Create a black image
        black_img = Image.new('RGB', (100, 100), color=(10, 10, 10))
        metrics = check_image_degradation(black_img)
        self.assertTrue(metrics["needs_low_light_correction"])
        
        # Create a bright image
        bright_img = Image.new('RGB', (100, 100), color=(200, 200, 200))
        metrics_bright = check_image_degradation(bright_img)
        self.assertFalse(metrics_bright["needs_low_light_correction"])
        
    def test_ocr_plate_validation(self):
        self.assertTrue(validate_plate_format("MH12AB1234"))
        self.assertTrue(validate_plate_format("DL3CAF5521"))
        self.assertFalse(validate_plate_format("INVALID_PLATE"))
        
    def test_rules_engine_helmet(self):
        detections = [
            {"label": "Motorcycle", "confidence": 0.9, "track_id": 1, "box": [0,0,10,10]},
            {"label": "Head_No_Helmet", "confidence": 0.95, "track_id": 2, "box": [0,0,5,5]}
        ]
        res = check_violations(detections)
        self.assertTrue(res["has_violation"])
        self.assertEqual(res["violation_type"], "Helmet Violation")
        
    def test_rules_engine_triple_riding(self):
        detections = [
            {"label": "Motorcycle", "confidence": 0.9, "track_id": 1, "box": [0,0,10,10]},
            {"label": "Rider_1", "confidence": 0.9, "track_id": 2, "box": [0,0,5,5]},
            {"label": "Rider_2", "confidence": 0.9, "track_id": 3, "box": [0,0,5,5]},
            {"label": "Rider_3", "confidence": 0.9, "track_id": 4, "box": [0,0,5,5]}
        ]
        res = check_violations(detections)
        self.assertTrue(res["has_violation"])
        self.assertEqual(res["violation_type"], "Triple Riding")

if __name__ == '__main__':
    unittest.main()
