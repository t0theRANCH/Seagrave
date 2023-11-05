import time

from pyobjus import autoclass, protocol
from api_requests import open_request


@protocol('UIImagePickerControllerDelegate')
class MyImagePickerDelegate:
    phone = None

    @protocol('UIImagePickerControllerDelegate')
    def imagePickerController_didFinishPickingMediaWithInfo_(self, picker, info):
        # This method is called when an image (or media) is picked.
        try:
            picker.dismissViewControllerAnimated_completion_(True, None)
            url = info.objectForKey_('UIImagePickerControllerImageURL')
            file_path = url.path
            file_path_str = str(file_path.UTF8String())
            self.phone.selected_file = file_path_str
            self.phone.upload_image()
        except Exception as e:
            import traceback
            crash_info = traceback.format_exc()
            open_request(name='log', data={'log_type': 'error', 'data': str(crash_info)})
            picker.dismissViewControllerAnimated_completion_(True, None)

    @protocol('UIImagePickerControllerDelegate')
    def imagePickerControllerDidCancel_(self, picker):
        # This method is called when the user cancels the picking action.
        # Typically, you'd just dismiss the picker:
        picker.dismissViewControllerAnimated_completion_(True, None)
