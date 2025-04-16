import os
from unittest.mock import patch

import cloudinary

from config import SECRET_KEY


def test_cloudinary_config():
    with patch.dict(os.environ, {
        "CLOUDINARY_CLOUD_NAME": "test_cloud_name",
        "CLOUDINARY_API_KEY": "test_api_key",
        "CLOUDINARY_API_SECRET": "test_api_secret"
    }):
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET")
        )
        assert cloudinary.config().cloud_name == "test_cloud_name"
        assert cloudinary.config().api_key == "test_api_key"
        assert cloudinary.config().api_secret == "test_api_secret"


def test_secret_key():
    with patch.dict(os.environ, {"SECRET_KEY": "test_secret_key"}):
        assert SECRET_KEY == "test_secret_key"
