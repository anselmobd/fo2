from pprint import pprint


class OperacoesDictList():

    def merge(self, inicial, merge, keys, fields_max):
        final = inicial.copy()
        for m_row in merge:

            typed_row = {}
            for field in m_row:
                value = m_row[field]
                val_type =  (
                    'key' if field in keys else
                    'str' if isinstance(value, str) else
                    'int'
                )
                if val_type not in typed_row:
                    typed_row[val_type] = {}
                typed_row[val_type][field] = value

            f_row = next(
                (
                    row
                    for row in final
                    if all(
                        [   typed_row['key'][field] == row[field]
                            for field in typed_row['key']
                        ]
                    )
                ),
                None
            )
            if f_row:
                for field in fields_max:
                    f_row[field] = max(f_row[field], m_row[field])
            else:
                final.append(m_row)
        return final