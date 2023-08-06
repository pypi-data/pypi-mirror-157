"""
Using the `authx_core.AuthXBasedView` decorator, we can consolidate the
endpoint signatures and reduce the number of repeated dependencies.

To use the `@AuthXBasedView` decorator, you need to:

     -  Create an APIRouter to which you will add the endpoints
     -  Create a class whose methods will be endpoints with shared depedencies, and decorate it with `@AuthXBasedView(router)`
     -  For each shared dependency, add a class attribute with a value of type `Depends`
     -  Replace use of the original "unshared" dependencies with accesses like `self.dependency`
"""

from authx_core.view._initial import _initial_view as authxInitialView
from authx_core.view._update import _update_view_signature as authxUpdateViewSignature
from authx_core.view._view import AuthXBasedView

__all__ = ["AuthXBasedView", "authxInitialView", "authxUpdateViewSignature"]
