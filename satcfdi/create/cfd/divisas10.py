from decimal import Decimal
from datetime import datetime, date, time
from collections.abc import Sequence
from ...cfdi import CFDI, XElement


class Divisas(CFDI):
    """
    Complemento al Comprobante Fiscal Digital (CFD) y Comprobante Fiscal Digital por Internet (CFDI) para identificar las operaciones de compra y venta de divisas que realizan los centros cambiarios y las casa de cambio; haciendo mención expresa de que los comprobantes se expiden por la “compra”, o bien, por la “venta” de divisas.
    """
    tag = '{http://www.sat.gob.mx/divisas}Divisas'
    version = '1.0'
    
    def __init__(
            self,
            tipo_operacion: str,
    ): 
        """
        Complemento al Comprobante Fiscal Digital (CFD) y Comprobante Fiscal Digital por Internet (CFDI) para identificar las operaciones de compra y venta de divisas que realizan los centros cambiarios y las casa de cambio; haciendo mención expresa de que los comprobantes se expiden por la “compra”, o bien, por la “venta” de divisas.
        
        :param tipo_operacion: Elemento para definir el tipo de operación realizada. venta o compra de divisas
        """
        
        super().__init__({
            'Version': self.version,
            'TipoOperacion': tipo_operacion,
        })
        
