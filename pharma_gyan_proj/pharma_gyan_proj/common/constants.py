from enum import Enum

TAG_SUCCESS = "SUCCESS"
TAG_FAILURE = "FAILURE"
TAG_GENERATE_OTP = "GENERATE_OTP"


class PromoCodeDiscountType(Enum):
    flat = "flat"
    percentage = "percentage"
    
class AdminUserPermissionType(Enum):
    viewUsers = "View Users"
    editUsers = "Edit Users"
    viewPromoCodes = "View PromoCodes"
    editPromoCodes = "Edit PromoCodes"
    viewContent = "View Content"
    editContent = "Edit Content"


BUCKET_NAME = "pharma-gyan-test-media"
    
