from streaming.scraper.api.models import Snapshots
from io import BytesIO
from PIL import Image
import imagehash
import hashlib
import mongoengine

class Snapshot:
    def __init__(self, url):
        self.url = url

    def create(self, data):
        try:
            dhash = str(imagehash.dhash(Image.open(BytesIO(data))))
            sha256 = hashlib.sha256(data).hexdigest()

            snapshot_output = Snapshots(url=self.url,sha256=sha256, dhash=dhash)
            snapshot_output.screenshot.put(data, content_type="image/png")
            snapshot_output.save()

            result = {"result": "success", "data": "Succesfully inserted snapshot result", "sha256":sha256, "dhash":dhash}

        except Exception as err:
            print(err)
            result = {"result": "failed", "data": "Failed to insert snapshot"}

        return result