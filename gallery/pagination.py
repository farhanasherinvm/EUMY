from rest_framework.pagination import PageNumberPagination

class GalleryPagination(PageNumberPagination):
    # Default number of images per page
    page_size = 12 
    # Allows client to specify page size via query (e.g., ?page_size=25)
    page_size_query_param = 'page_size' 
    # Maximum page size allowed
    max_page_size = 200