from PIL import Image, ExifTags
import numpy as np


class RotatedImage:
    def __init__(self, image_path, site):
        self.orientation_rotation_mapping = {'2': [self.flip], '3': [self.rotate_180], '4': [self.flip, self.rotate_180],
                                             '5': [self.flip, self.rotate_cw], '6': [self.rotate_cw],
                                             '7': [self.flip, self.rotate_ccw], '8': [self.rotate_ccw]}
        self.image_path = image_path
        self.site = site
        self.image_in = Image.open(image_path)
        self.image_in_array = np.asarray(Image.open(image_path))
        self.orientation = self.get_orientation()
        self.image_out = None
        self.image_out_path = ''

    def get_orientation(self):
        exif = {ExifTags.TAGS[k]: v for k, v in self.image_in.getexif().items() if k in ExifTags.TAGS}
        return exif.get('Orientation', None)

    def rotate(self):
        if not self.orientation or self.orientation == '1':
            return False
        for func in self.orientation_rotation_mapping[str(self.orientation)]:
            self.image_in_array = func(self.image_in_array)
        self.image_out = Image.fromarray(self.image_in_array)
        self.image_out.save(f"assets/{self.site}.jpg")
        self.image_out_path = f"assets/{self.site}.jpg"

    @staticmethod
    def flip(image):
        return np.fliplr(image)

    @staticmethod
    def rotate_cw(image):
        return np.rot90(image, -1)

    @staticmethod
    def rotate_ccw(image):
        return np.rot90(image)

    @staticmethod
    def rotate_180(image):
        return np.rot90(image, 2)


"""img = RotatedImage('/home/tyson/PycharmProjects/FormRip/assets/20220926_161748.jpg')
img.rotate()
img.save()"""

