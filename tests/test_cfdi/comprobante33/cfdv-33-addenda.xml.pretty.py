{'Addenda': {'AddendaBuzonFiscal': {'CFD': {'totalConLetra': 'Cuarenta  mil '
                                                             'seiscientos '
                                                             'pesos 00/100 '
                                                             'M.N.'},
                                    'TipoDocumento': {'_text': 'Hola',
                                                      'descripcion': 'Factura',
                                                      'nombreCorto': 'FAC'},
                                    'version': '2.0'},
             'AddendaEmisor': {'AddendaMG': {'MG': {'descripcion': ' TICKET '
                                                                   'No: '
                                                                   '1724993394380039641809 '
                                                                   'TR No: '
                                                                   '6829'}},
                               'InformacionAdicionalPuntoDeVenta': CFDI({})}},
 'Certificado': '',
 'CfdiRelacionados': {'CfdiRelacionado': ['ED1752FE-E865-4FF2-BFE1-0F552E770DC9'],
                      'TipoRelacion': Code('02', 'Nota de débito de los documentos relacionados')},
 'Conceptos': [{'Cantidad': Decimal('1.5'),
                'ClaveProdServ': Code('01010101', 'No existe en el catálogo'),
                'ClaveUnidad': Code('C81', 'Radián'),
                'CuentaPredial': '51888',
                'Descripcion': 'ACERO',
                'Importe': Decimal('2250000'),
                'Impuestos': {'Retenciones': {'001|Tasa|0.300000': {'Base': Decimal('2250000'),
                                                                    'Importe': Decimal('247500'),
                                                                    'Impuesto': Code('001', 'ISR'),
                                                                    'TasaOCuota': Decimal('0.300000'),
                                                                    'TipoFactor': Code('Tasa', None)}},
                              'Traslados': {'002|Tasa|1.600000': {'Base': Decimal('2250000'),
                                                                  'Importe': Decimal('360000'),
                                                                  'Impuesto': Code('002', 'IVA'),
                                                                  'TasaOCuota': Decimal('1.600000'),
                                                                  'TipoFactor': Code('Tasa', None)}}},
                'NoIdentificacion': '00001',
                'Unidad': 'TONELADA',
                'ValorUnitario': Decimal('1500000')}],
 'CondicionesDePago': 'CONDICIONES',
 'Confirmacion': 'Az123',
 'Descuento': Decimal('0.00'),
 'Emisor': {'Nombre': 'Esta es una demostración',
            'RegimenFiscal': Code('622', 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras'),
            'Rfc': ' AAA010101AAA'},
 'Fecha': datetime.datetime(2017, 5, 20, 23, 23, 59),
 'Folio': '123ABC',
 'FormaPago': Code('02', 'Cheque nominativo'),
 'Impuestos': {'Retenciones': {'001': {'Importe': Decimal('247000'),
                                       'Impuesto': Code('001', 'ISR')},
                               '003': {'Importe': Decimal('500'),
                                       'Impuesto': Code('003', 'IEPS')}},
               'TotalImpuestosRetenidos': Decimal('247500'),
               'TotalImpuestosTrasladados': Decimal('360000'),
               'Traslados': {'002|Tasa|1.600000': {'Importe': Decimal('360000'),
                                                   'Impuesto': Code('002', 'IVA'),
                                                   'TasaOCuota': Decimal('1.600000'),
                                                   'TipoFactor': Code('Tasa', None)}}},
 'LugarExpedicion': Code('45079', None),
 'MetodoPago': Code('PUE', 'Pago en una sola exhibición'),
 'Moneda': Code('MXN', 'Peso Mexicano'),
 'NoCertificado': '40001000000300000337',
 'Receptor': {'Nombre': 'Juanito Bananas De la Sierra',
              'NumRegIdTrib': '987654321',
              'ResidenciaFiscal': Code('MEX', 'México'),
              'Rfc': 'BASJ600902KL9',
              'UsoCFDI': Code('G03', 'Gastos en general')},
 'Sello': '',
 'Serie': 'A',
 'SubTotal': Decimal('1000'),
 'TipoCambio': Decimal('1.0'),
 'TipoDeComprobante': Code('I', 'Ingreso'),
 'Total': Decimal('1500'),
 'Version': '3.3'}