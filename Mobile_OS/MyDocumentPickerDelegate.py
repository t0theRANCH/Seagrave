from pyobjus import protocol


@protocol('UIDocumentPickerDelegate')  # This decorator marks the class as a delegate
class MyDocumentPickerDelegate:
    phone = None

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
        first_url = urls.firstObject()
        self.phone.selected_file = first_url.absoluteString()
        self.phone.upload_image()

