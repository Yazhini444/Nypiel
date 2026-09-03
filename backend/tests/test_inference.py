import io
import unittest
from PIL import Image
from app import inference, recommendations


class TestModelInference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inference.load_models()

    def test_skin_type_model_loaded(self):
        self.assertIsNotNone(inference._skin_type_model)
        self.assertEqual(len(inference.SKIN_TYPES), 4)
        self.assertIn("combination", inference.SKIN_TYPES)
        self.assertIn("dry", inference.SKIN_TYPES)
        self.assertIn("normal", inference.SKIN_TYPES)
        self.assertIn("oily", inference.SKIN_TYPES)

    def test_concern_model_loaded(self):
        self.assertIsNotNone(inference._concern_model)

    def test_predict_skin_type_output(self):
        img = Image.new("RGB", (224, 224), color=(200, 180, 160))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        res = inference.predict_skin_type(buf.getvalue())
        self.assertIn("label", res)
        self.assertIn("confidence", res)
        self.assertIn(res["label"], inference.SKIN_TYPES)
        self.assertGreaterEqual(res["confidence"], 0.0)
        self.assertLessEqual(res["confidence"], 1.0)

    def test_predict_skin_concerns_output(self):
        img = Image.new("RGB", (320, 320), color=(200, 180, 160))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        res = inference.predict_skin_concerns(buf.getvalue())
        self.assertIsInstance(res, list)

    def test_recommendations_generation(self):
        concerns = [
            {"label": "acne", "confidence": 0.85, "box": [0.1, 0.1, 0.2, 0.2]},
            {"label": "dark_spots", "confidence": 0.75, "box": [0.3, 0.3, 0.1, 0.1]},
        ]
        recs = recommendations.build_recommendations("oily", concerns)
        self.assertGreater(len(recs), 0)
        ingredients = [r["ingredient"] for r in recs]
        self.assertIn("Salicylic Acid", ingredients)


if __name__ == "__main__":
    unittest.main()
