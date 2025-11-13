# gallery/pagination.py (Create a new file or put this at the top of your views.py)
from rest_framework.pagination import PageNumberPagination

class TeamMemberPagination(PageNumberPagination):
    # Default number of items per page
    page_size = 10 
    # Parameter for client to specify page size (e.g., ?page_size=20)
    page_size_query_param = 'page_size' 
    # Maximum size the client can request
    max_page_size = 100