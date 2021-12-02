from .docs import urlpatterns as docs_urlpatterns
from .documented import urlpatterns as documented_urlpatterns
from .undocumented import urlpatterns as undocumented_urlpatterns


urlpatterns = documented_urlpatterns + undocumented_urlpatterns + docs_urlpatterns
