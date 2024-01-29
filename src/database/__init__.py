"""
Load database modules
"""

# Auth
from .user import UserModel, ClassroomMember, ClassroomMemberType, \
                  SubscriptionStatus, EnumSubscriptionStatus, \
                  MembershipType, EnumMembershipType, \
                  PrivilegeType, EnumPrivilegeType, \
                  UserStatus, EnumUserStatus

from .token import TokenModel, TokenType, EnumTokenType
from .jwtblocklist import JWTBlocklistModel, JWTType, EnumJWTType

# Misc
from .comment import CommentModel
from .classroom import ClassroomModel
from .submission import SubmissionModel
from .assignment import AssignmentModel

# Uploads
from .image import ImageModel, ImageUploadStatus, EnumImageUploadStatus
from .discount import DiscountModel
from .textbook import TextbookModel, TextbookStatus, EnumTextbookStatus, TextbookUploadStatus, EnumTextbookUploadStatus
from .submissionsnippet import SubmissionSnippetModel, SnippetUploadStatus, EnumSnippetUploadStatus

from .sale import SaleModel, SaleInfo, SaleType, EnumSaleType

# Assocations
from .assotiation import user_textbook_assotiation, \
                         classroom_textbook_assotiation, \
                         assignment_textbook_assotiation, \
                         sale_textbook_assotiation, \
                         classroom_user_assotiation, ClassroomMemberRole, EnumClassroomMemberRole
