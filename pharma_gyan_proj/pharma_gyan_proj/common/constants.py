from enum import Enum

TAG_SUCCESS = "SUCCESS"
TAG_FAILURE = "FAILURE"
TAG_GENERATE_OTP = "GENERATE_OTP"


class PromoCodeDiscountType(Enum):
    flat = "flat"
    percentage = "percentage"
