from django.urls import path
from .views import PostsList, PostDetail, PostCreate, PostUpdate, PostDelete, PostSearch, ProfileUpdate, \
    CategoryListView, subscribe
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(60)(PostsList.as_view()), name='post_list'),
    path('search/', cache_page(60)(PostSearch.as_view()), name='post_search'),
    path('<int:pk>', cache_page(60)(PostDetail.as_view()), name='post_detail'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('profile/<int:pk>/edit', ProfileUpdate.as_view(), name='profile_update'),
    path('categories/<int:pk>', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/subscribe', subscribe, name='subscribe')
]
