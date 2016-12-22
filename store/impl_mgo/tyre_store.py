#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikem#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from store.base_mongo_store import BaseMgoStore


class TyreStore(BaseMgoStore):
    def __init__(self):
        self.mongo_url, self.db_name, self.coll_name = self.load_mongo_conf("tyre")
        BaseMgoStore.__init__(self, self.mongo_url)




if __name__ == '__main__':
    s = TyreStore()
    s.get({'itemId':'f00fe32281e5448dae5e519603f5c7cf'})
