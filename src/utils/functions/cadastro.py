from pprint import pprint
from validate_docbr import CNPJ as docbr_CNPJ


class CNPJ(docbr_CNPJ):
    def validate(self, doc: str = "") -> bool:
        self.cnpj = "0" * 14
        doc = self._only_digits(doc)
        if super(CNPJ, self).validate(doc):
            self.cnpj = doc
            return True
        else:
            if len(doc) <= 8:
                idoc = int(f"0{doc}")
                if idoc == 0:
                    return False
                fdoc = f"{idoc:08}"
                self.cnpj = fdoc + "0001"
                digito = self._generate_first_digit(self.cnpj)
                self.cnpj = self.cnpj + digito
                digito = self._generate_second_digit(self.cnpj)
                self.cnpj = self.cnpj + digito
                return True
            else:
                return False

    def mask(self, doc: str = '') -> str:
        doc = self._only_digits(doc)
        return super(CNPJ, self).mask(doc)
