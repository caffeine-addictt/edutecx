"""
Load database modules
"""

# Auth
from .user import UserModel
from .token import TokenModel
from .jwtblocklist import JWTBlocklistModel

# Misc
from .comment import CommentModel
from .classroom import ClassroomModel
from .submission import SubmissionModel
from .assignment import AssignmentModel

# Uploads
from .image import ImageModel
from .textbook import TextbookModel

from .sale import SaleModel
