#import <UIKit/UIKit.h>
#import <PDFKit/PDFKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface PDFModalViewController : UIViewController

- (instancetype)initWithPDFAtPath:(NSString *)path;

@end

NS_ASSUME_NONNULL_END

