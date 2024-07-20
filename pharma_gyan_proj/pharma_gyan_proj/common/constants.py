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
    viewCourses = "View Courses"
    editCourses = "Edit Courses"
    viewPackages = "View Packages"
    editPackages = "Edit Packages"
    viewChapters = "View Chapters"
    editChapter = "Edit Chapter"
    editEntityTag = "Edit Entity Tag"
    viewEntityTag = "View Entity Tag"
    editTopic = "editTopic"
    viewTopics = "viewTopics"


BUCKET_NAME = "pharma-gyan-test-media"

ACTIVE_CHAPTER_CHECK = False
    
