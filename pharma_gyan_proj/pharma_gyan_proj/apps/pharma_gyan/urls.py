from django.urls import path, include
from pharma_gyan_proj.apps.pharma_gyan import views

urlpatterns = [
    path('editor/adminLogin', views.admin_login),
    path('editor/', views.editor),
    path('editor/dashboard/', views.dashboard),
    path('editor/promoCode', views.promo_code),
    path('editor/clonePromoCode', views.edit_promo_code),
    path('editor/viewPromoCode', views.view_promo_code),
    path("editor/upsertPromoCode/", views.upsert_promo_code),
    path('editor/entityTag', views.entity_tag),
    path('editor/viewEntityTag', views.view_entity_tag),
    path('editor/cloneEntityTag', views.clone_entity_tag),
    path("editor/upsertEntityTag/", views.upsert_entity_tag),
    path("editor/addChapter/", views.add_chapter),
    path("editor/upsertChapter/", views.upsert_chapter),
    path("editor/secureLogin/", views.secure_login),
    path("editor/dumpDatabase/", views.dump_database),
    path("editor/addUser/", views.addUser),
    path("editor/editUser/", views.editUser),
    path("editor/viewUsers/", views.viewUsers),
    path("editor/upsertUser/", views.upsertUser),
    path("editor/deleteUser/<str:userId>/", views.deleteUser),
    path("editor/deactivatePromoCode/<str:uniqueId>/", views.deactivate_promo_code),
    path("editor/activatePromoCode/<str:uniqueId>/", views.activate_promo_code),
    path("editor/deactivateEntityTag/<str:uniqueId>/", views.deactivate_entity_tag),
    path("editor/activateEntityTag/<str:uniqueId>/", views.activate_entity_tag),
    path("editor/addMedia/", views.add_media),
    path("editor/addCourse/", views.addCourse),
    path("editor/viewCourses/", views.viewCoursesV2),
    path("editor/upsertCourse/", views.upsertCourse),
    path("editor/upsertCourseV2/", views.upsertCourseV2),
    path("editor/deactivateCourse/<str:uniqueId>/", views.deactivate_course),
    path("editor/activateCourse/<str:uniqueId>/", views.activate_course),
    path("editor/editCourse/", views.editCourseV2),
    path("editor/getCourseTreeJson/<str:uniqueId>/", views.get_course_tree_json),
    path("editor/addTopicChapters/", views.addTopicChapters),
    path("editor/upsertTopic/", views.upsertTopic),
    # path("editor/previewChapterContent/<str:uniqueId>/", views.preview_chapter_content),
    path("editor/previewChapterContent/", views.preview_chapter_content),
    path("editor/activateCourseV2", views.activate_course_v2),
    path("editor/deactivateCourseV2", views.deactivate_course_v2),
    # package
    path("editor/addPackage/", views.addPackage),
    path("editor/viewPackages/", views.viewPackages),
    path("editor/editPackage/", views.editPackage),
    path("editor/upsertPackage/", views.upsertPackage),
    path("editor/activatePackage", views.activate_package),
    path("editor/deactivatePackage", views.deactivate_package),
]