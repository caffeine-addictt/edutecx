"""
Sale Endpoint
"""

from src import limiter
from src.utils.http import HTTPStatusCode
from src.database import SaleModel, UserModel
from src.service.auth_provider import require_login
from src.utils.api import (
  SaleGetRequest, SaleGetReply, _SaleGetData,
  GenericReply
)
from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/sale'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
@require_login
def sale_get_api(user: UserModel):
  req = SaleGetRequest(request)

  sale = SaleModel.query.filter(SaleModel.id == req.sale_id).first()
  if (not sale) or (not isinstance(sale, SaleModel)):
    return GenericReply(
      message = 'Unable to locate sale',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if (user.privilege != 'Admin') or (sale.user_id != user.id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  
  return SaleGetReply(
    message = 'Successfully fetched sale',
    status = HTTPStatusCode.OK,
    data = _SaleGetData(
      sale_id = sale.id,
      user_id =  user.id,
      textbook_ids = [ i.split(':')[0] for i in sale.textbook_ids.split(',') ]
    )
  ).to_dict(), HTTPStatusCode.OK
