import os
import unittest

from app import inference


class TestModelPaths(unittest.TestCase):
    def test_uses_actual_backend_root_model_files(self):
        self.assertTrue(os.path.exists(inference.SKIN_TYPE_WEIGHTS))
        self.assertTrue(os.path.exists(inference.CONCERN_WEIGHTS))
        self.assertEqual(os.path.basename(inference.SKIN_TYPE_WEIGHTS), "nypiel_skin_type_model.pth")
        self.assertEqual(os.path.basename(inference.CONCERN_WEIGHTS), "best.pt")


if __name__ == "__main__":
    unittest.main()
