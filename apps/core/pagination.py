"""
Custom pagination classes.
"""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Standard pagination with 10 items per page."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """Large pagination with 25 items per page."""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class SmallPagination(PageNumberPagination):
    """Small pagination with 5 items per page."""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50
