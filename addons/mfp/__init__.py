from . import models
from . import controllers
from . import wizard


# 安裝時執行
def post_init_hook(env):
    # 對聯絡人進行Code編碼
    domain = ['&', '&',
              ('user_ids', '=', False),
              ('company_id', '=', False),
              ('parent_id', '=', False)]
    partner_model = env['res.partner'].search(domain)
    partner_model.check_and_update_code()
