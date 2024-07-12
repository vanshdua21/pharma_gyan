from enum import Enum

TAG_SUCCESS = "SUCCESS"
TAG_FAILURE = "FAILURE"
TAG_GENERATE_OTP = "GENERATE_OTP"


class PromoCodeDiscountType(Enum):
    flat = "flat"
    percentage = "percentage"
# class level(Enum):
#     one = '1',
#     two = 2,
#     three = 3,
#     four = 4,
#     five = 5
class AdminUserPermissionType(Enum):
    viewUsers = "View Users"
    editUsers = "Edit Users"
    viewPromoCodes = "View PromoCodes"
    editPromoCodes = "Edit PromoCodes"
    viewContent = "View Content"
    editContent = "Edit Content"
    viewChapters = "View Chapters"
    editChapter = "Edit Chapter"


BUCKET_NAME = "pharma-gyan-test-media"
    
