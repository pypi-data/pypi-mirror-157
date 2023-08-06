import asyncio
import os.path

import aiohttp

from docparser.core.behavior_base import BehaviorBase
from docparser.core.tools import Tools


class TextRepairBehavior(BehaviorBase):
    class_index = 0

    def data_processing(self, ref_data, data: list, error: list, config: dict, logger, additional) -> dict:

        conf = config.get("text_repair")

        if 'file' not in additional or conf is None:
            return additional

        sub_conf = conf.get('subs')

        if sub_conf is None:
            return additional

        sub_conf = [Tools.init_regex(item) for item in sub_conf]

        lines = asyncio.run(self.__convert(additional, conf))

        if lines:

            if lines and isinstance(lines, list):
                for line in lines:
                    for sub in sub_conf:
                        res = Tools.match_value(line, sub)
                        if res is not None and isinstance(res, dict):
                            for k, v in res.items():
                                data[k] = v
                                if k == conf.get('stop'):
                                    return additional

        return additional

    async def __convert(self, additional, conf):

        file = additional.get('file')
        file_suffix = os.path.splitext(file)
        if file_suffix[1].lower() != '.xlsx':
            return None
        pdf_url = conf.get("pdf_api")
        url_params = {"filepath": f'{file_suffix[0]}.pdf', "doctype": 'txt'}
        header = {
            "Content-type": "application/json"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(pdf_url, headers=header, json=url_params) as res:
                    if res.ok:
                        res_content = await res.json(content_type=None)
                        if res_content.get("status"):
                            return res_content.get("data")
        except Exception:
            pass


# if __name__ == '__main__':
#     test_data = {"test1": "NINGBO, CHINA", "test2": "DISHMAN-PHARMACEUTICAL-",
#                  "address":
#                      {"column": ["col1", "col2", "col3", "col4"],
#                       "rows": [
#                           ["aaedfkkk", "sc", "ITAAPS", "LIA NYU NGANG1, USA"],
#                           ["12f", "HI", "mckdg", "IA"]
#                       ]
#                       }}
#     TextRepairBehavior().data_processing(
#         None, test_data,
#         [],
#         {
#             "text_repair": {
#                 "pdf_api": "http://192.168.4.62:18008/api/converter_to_txt",
#                 "stop": "DestinationPortName",
#                 "subs": [
#                     [
#                         "VESSEL\\s*:\\s*(?P<VesselName>[\\w\\W]*?)\\s*VOYAGE\\s*:\\s*"
#                     ],
#                     [
#                         "OPERATIONAL\\s*DISCH\\.\\s*PORT\\s*:\\s*(?P<DestinationPortName>[\\w\\W]*)$"
#                     ]
#                 ]
#             }
#         }, None, {'file':'/var/storage/email/2022/06/26/bizmx40t1656216758teu9fyzio/noa-cmacgm-noticeofarrival-cmacgmalexandervonhumboldt-0tun0w1ma-at220626040637-220695-000301.xlsx'}
#     )
#
#     print(test_data)
