from collections import OrderedDict, namedtuple

from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.compat import coreapi, coreschema
from rest_framework.utils.urls import remove_query_param, replace_query_param
from django.core.paginator import Paginator as DjangoPaginator
from django.core.paginator import InvalidPage
from django.template import loader
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


##################################################################################

Cursor = namedtuple('Cursor', ['offset', 'reverse', 'position'])
PageLink = namedtuple('PageLink', ['url', 'number', 'is_active', 'is_break'])

PAGE_BREAK = PageLink(url=None, number=None, is_active=False, is_break=True)


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret


def _get_displayed_page_numbers(current, final):
    """
    This utility function determines a list of page numbers to display.
    This gives us a nice contextually relevant set of page numbers.

    For example:
    current=14, final=16 -> [1, None, 13, 14, 15, 16]

    This implementation gives one page to each side of the cursor,
    or two pages to the side when the cursor is at the edge, then
    ensures that any breaks between non-continuous page numbers never
    remove only a single page.

    For an alternative implementation which gives two pages to each side of
    the cursor, eg. as in GitHub issue list pagination, see:

    https://gist.github.com/tomchristie/321140cebb1c4a558b15
    """
    assert current >= 1
    assert final >= current

    if final <= 5:
        return list(range(1, final + 1))

    # We always include the first two pages, last two pages, and
    # two pages either side of the current page.
    included = {1, current - 1, current, current + 1, final}

    # If the break would only exclude a single page number then we
    # may as well include the page number instead of the break.
    if current <= 4:
        included.add(2)
        included.add(3)
    if current >= final - 3:
        included.add(final - 1)
        included.add(final - 2)

    # Now sort the page numbers and drop anything outside the limits.
    included = [
        idx for idx in sorted(list(included))
        if 0 < idx <= final
    ]

    # Finally insert any `...` breaks
    if current > 4:
        included.insert(1, None)
    if current < final - 3:
        included.insert(len(included) - 1, None)
    return included


def _get_page_links(page_numbers, current, url_func):
    """
    Given a list of page numbers and `None` page breaks,
    return a list of `PageLink` objects.
    """
    page_links = []
    for page_number in page_numbers:
        if page_number is None:
            page_link = PAGE_BREAK
        else:
            page_link = PageLink(
                url=url_func(page_number),
                number=page_number,
                is_active=(page_number == current),
                is_break=False
            )
        page_links.append(page_link)
    return page_links


class OncePageNumberPagination(object):
    """
    A simple page number based style that supports page numbers as
    query parameters. For example:

    http://api.example.org/accounts/?page=4
    http://api.example.org/accounts/?page=4&page_size=100
    """
    # The default page size.
    # Defaults to `None`, meaning pagination is disabled.
    page_size = 15

    django_paginator_class = DjangoPaginator

    # Client can control the page using this query parameter.
    page_query_param = 'page'
    page_query_description = _('A page number within the paginated result set.')

    # Client can control the page size using this query parameter.
    # Default is 'None'. Set to eg 'page_size' to enable usage.
    page_size_query_param = None
    page_size_query_description = _('Number of results to return per page.')

    # Set to an integer to limit the maximum page size the client may request.
    # Only relevant if 'page_size_query_param' has also been set.
    max_page_size = None

    last_page_strings = ('last',)

    template = 'rest_framework/pagination/numbers.html'

    invalid_page_message = _('Invalid page.')

    def __init__(self, page_size):
        self.page_size = page_size

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def get_html_context(self):
        base_url = self.request.build_absolute_uri()

        def page_number_to_url(page_number):
            if page_number == 1:
                return remove_query_param(base_url, self.page_query_param)
            else:
                return replace_query_param(base_url, self.page_query_param, page_number)

        current = self.page.number
        final = self.page.paginator.num_pages
        page_numbers = _get_displayed_page_numbers(current, final)
        page_links = _get_page_links(page_numbers, current, page_number_to_url)

        return {
            'previous_url': self.get_previous_link(),
            'next_url': self.get_next_link(),
            'page_links': page_links
        }

    def to_html(self):
        template = loader.get_template(self.template)
        context = self.get_html_context()
        return template.render(context)

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        fields = [
            coreapi.Field(
                name=self.page_query_param,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Page',
                    description=force_text(self.page_query_description)
                )
            )
        ]
        if self.page_size_query_param is not None:
            fields.append(
                coreapi.Field(
                    name=self.page_size_query_param,
                    required=False,
                    location='query',
                    schema=coreschema.Integer(
                        title='Page size',
                        description=force_text(self.page_size_query_description)
                    )
                )
            )
        return fields
