from pyobjus import protocol
from urllib.parse import unquote, urlparse
from api_requests import open_request


@protocol('UIDocumentPickerDelegate')  # This decorator marks the class as a delegate
class MyDocumentPickerDelegate:
    phone = None

    def __init__(self):
        self.urls = None

    @protocol('UIDocumentPickerDelegate')
    def documentPickerWasCancelled_(self, controller):
        """
        Delegate called when the user cancels the document picker.
        """
        controller.dismissViewControllerAnimated_completion_(True, None)

    @protocol('UIDocumentPickerDelegate')
    def documentPicker_didPickDocumentsAtURLs_(self, controller, urls):
        # This method gets called when the user picks documents
        # Handle the picked documents here. 'urls' is a list of file URLs.
        try:
            controller.dismissViewControllerAnimated_completion_(True, None)
            self.urls = urls
            self.phone.main_controller.view.scrim_on(message='Uploading Image')
            self.phone.main_controller.view.async_task(self.parse_url)
        except Exception as e:
            import traceback
            crash_info = traceback.format_exc()
            open_request(name='log', data={'log_type': 'error', 'data': str(crash_info)})
            controller.dismissViewControllerAnimated_completion_(True, None)
        finally:
            self.urls = None

    def parse_url(self):
        url = self.urls.firstObject()
        url_string = url.absoluteString.UTF8String()
        parsed_url = urlparse(url_string)
        file_name = unquote(parsed_url.path)
        self.phone.selected_file_name = file_name.split("/")[-1]
        self.phone.selected_file = url.absoluteString
        self.phone.upload_image()
