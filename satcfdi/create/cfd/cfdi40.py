from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from . import pago20
from ..compute import make_impuestos, rounder, make_impuestos_dr, make_impuesto, \
    make_impuestos_dr_parcial
from ...cfdi import CFDI, XElement, get_timezone
from ...create import Issuer
from ...utils import iterate

_impuestos = {
    "ISR": "001",
    "IVA": "002",
    "IEPS": "003",
}


class Impuesto(XElement):
    """
    http://www.sat.gob.mx/cfd/4
    Nodo requerido para la información detallada de un traslado de impuesto específico.
    """

    def __init__(
            self,
            impuesto: str,
            tipo_factor: str,
            tasa_o_cuota: Decimal | int = None,
            importe: Decimal | int = None,
            base: Decimal | int = None,
    ):
        """
        Nodo requerido para la información detallada de un impuesto específico.

        :param base: Atributo requerido para señalar la suma de los atributos Base de los conceptos del impuesto trasladado. No se permiten valores negativos.
        :param impuesto: Atributo requerido para señalar la clave del tipo de impuesto trasladado.
        :param tipo_factor: Atributo requerido para señalar la clave del tipo de factor que se aplica a la base del impuesto.
        :param tasa_o_cuota: Atributo condicional para señalar el valor de la tasa o cuota del impuesto que se traslada por los conceptos amparados en el comprobante.
        :param importe: Atributo condicional para señalar la suma del importe del impuesto trasladado, agrupado por impuesto, TipoFactor y TasaOCuota. No se permiten valores negativos.
        """

        super().__init__({
            'Base': base,
            'Impuesto': _impuestos.get(impuesto, impuesto),
            'TipoFactor': tipo_factor,
            'TasaOCuota': tasa_o_cuota,
            'Importe': importe,
        })

    @classmethod
    def parse(cls, impuesto: str) -> 'Impuesto':
        parts = impuesto.split("|")
        return cls(
            impuesto=parts[0],
            tipo_factor=parts[1],
            tasa_o_cuota=Decimal(parts[2]) if len(parts) > 2 else None
        )


class CfdiRelacionados(XElement):
    """
    http://www.sat.gob.mx/cfd/4
    Nodo opcional para precisar la información de los comprobantes relacionados.
    """

    def __init__(
            self,
            tipo_relacion: str,
            cfdi_relacionado: str | Sequence[str],
    ):
        """
        Nodo opcional para precisar la información de los comprobantes relacionados.

        :param tipo_relacion: Atributo requerido para indicar la clave de la relación que existe entre éste que se está generando y el o los CFDI previos.
        :param cfdi_relacionado: Nodo requerido para precisar la información de los comprobantes relacionados.
        """

        super().__init__({
            'TipoRelacion': tipo_relacion,
            'CfdiRelacionado': cfdi_relacionado,
        })


class InformacionGlobal(XElement):
    """
    http://www.sat.gob.mx/cfd/4
    Nodo condicional para precisar la información relacionada con el comprobante global.
    """

    def __init__(
            self,
            periodicidad: str,
            meses: str,
            ano: int,
    ):
        """
        Nodo condicional para precisar la información relacionada con el comprobante global.

        :param periodicidad: Atributo requerido para expresar el período al que corresponde la información del comprobante global.
        :param meses: Atributo requerido para expresar el mes o los meses al que corresponde la información del comprobante global.
        :param ano: Atributo requerido para expresar el año al que corresponde la información del comprobante global.
        """

        super().__init__({
            'Periodicidad': periodicidad,
            'Meses': meses,
            'Año': ano,
        })


class Parte(XElement):
    """
    http://www.sat.gob.mx/cfd/4
    Nodo opcional para expresar las partes o componentes que integran la totalidad del concepto expresado en el comprobante fiscal digital por Internet.
    """

    def __init__(
            self,
            clave_prod_serv: str,
            cantidad: Decimal | int,
            descripcion: str,
            no_identificacion: str = None,
            unidad: str = None,
            valor_unitario: Decimal | int = None,
            importe: Decimal | int = None,
            informacion_aduanera: str | Sequence[str] = None,
    ):
        """
        Nodo opcional para expresar las partes o componentes que integran la totalidad del concepto expresado en el comprobante fiscal digital por Internet.

        :param clave_prod_serv: Atributo requerido para expresar la clave del producto o del servicio amparado por la presente parte. Es requerido y deben utilizar las claves del catálogo de productos y servicios, cuando los conceptos que registren por sus actividades correspondan con dichos conceptos.
        :param cantidad: Atributo requerido para precisar la cantidad de bienes o servicios del tipo particular definido por la presente parte.
        :param descripcion: Atributo requerido para precisar la descripción del bien o servicio cubierto por la presente parte.
        :param no_identificacion: Atributo opcional para expresar el número de serie, número de parte del bien o identificador del producto o del servicio amparado por la presente parte. Opcionalmente se puede utilizar claves del estándar GTIN.
        :param unidad: Atributo opcional para precisar la unidad de medida propia de la operación del emisor, aplicable para la cantidad expresada en la parte. La unidad debe corresponder con la descripción de la parte.
        :param valor_unitario: Atributo opcional para precisar el valor o precio unitario del bien o servicio cubierto por la presente parte. No se permiten valores negativos.
        :param importe: Atributo opcional para precisar el importe total de los bienes o servicios de la presente parte. Debe ser equivalente al resultado de multiplicar la cantidad por el valor unitario expresado en la parte. No se permiten valores negativos.
        :param informacion_aduanera: Nodo opcional para introducir la información aduanera aplicable cuando se trate de ventas de primera mano de mercancías importadas o se trate de operaciones de comercio exterior con bienes o servicios.
        """

        super().__init__({
            'ClaveProdServ': clave_prod_serv,
            'Cantidad': cantidad,
            'Descripcion': descripcion,
            'NoIdentificacion': no_identificacion,
            'Unidad': unidad,
            'ValorUnitario': valor_unitario,
            'Importe': importe,
            'InformacionAduanera': informacion_aduanera,
        })


class ACuentaTerceros(XElement):
    """
    http://www.sat.gob.mx/cfd/4
    Nodo opcional para registrar información del contribuyente Tercero, a cuenta del que se realiza la operación.
    """

    def __init__(
            self,
            rfc_a_cuenta_terceros: str,
            nombre_a_cuenta_terceros: str,
            regimen_fiscal_a_cuenta_terceros: str,
            domicilio_fiscal_a_cuenta_terceros: str,
    ):
        """
        Nodo opcional para registrar información del contribuyente Tercero, a cuenta del que se realiza la operación.

        :param rfc_a_cuenta_terceros: Atributo requerido para registrar la Clave del Registro Federal de Contribuyentes del contribuyente Tercero, a cuenta del que se realiza la operación.
        :param nombre_a_cuenta_terceros: Atributo requerido para registrar el nombre, denominación o razón social del contribuyente Tercero correspondiente con el Rfc, a cuenta del que se realiza la operación.
        :param regimen_fiscal_a_cuenta_terceros: Atributo requerido para incorporar la clave del régimen del contribuyente Tercero, a cuenta del que se realiza la operación.
        :param domicilio_fiscal_a_cuenta_terceros: Atributo requerido para incorporar el código postal del domicilio fiscal del Tercero, a cuenta del que se realiza la operación.
        """

        super().__init__({
            'RfcACuentaTerceros': rfc_a_cuenta_terceros,
            'NombreACuentaTerceros': nombre_a_cuenta_terceros,
            'RegimenFiscalACuentaTerceros': regimen_fiscal_a_cuenta_terceros,
            'DomicilioFiscalACuentaTerceros': domicilio_fiscal_a_cuenta_terceros,
        })


class Concepto(XElement):
    """
    http://www.sat.gob.mx/cfd/4
    Nodo requerido para registrar la información detallada de un bien o servicio amparado en el comprobante.
    """

    def __init__(
            self,
            clave_prod_serv: str,
            cantidad: Decimal | int,
            clave_unidad: str,
            descripcion: str,
            valor_unitario: Decimal | int,
            objeto_imp: str = None,
            no_identificacion: str = None,
            unidad: str = None,
            descuento: Decimal | int = None,
            a_cuenta_terceros: ACuentaTerceros | dict = None,
            informacion_aduanera: str | Sequence[str] = None,
            cuenta_predial: str | Sequence[str] = None,
            complemento_concepto: CFDI | Sequence[CFDI] = None,
            parte: Parte | Sequence[Parte | dict] = None,
            traslados: Impuesto | str | Sequence[Impuesto | str | dict] = None,
            retenciones: Impuesto | str | Sequence[Impuesto | str | dict] = None,
            _traslados_incluidos: bool = False
    ):
        """
        Nodo requerido para registrar la información detallada de un bien o servicio amparado en el comprobante.

        :param clave_prod_serv: Atributo requerido para expresar la clave del producto o del servicio amparado por el presente concepto. Es requerido y deben utilizar las claves del catálogo de productos y servicios, cuando los conceptos que registren por sus actividades correspondan con dichos conceptos.
        :param cantidad: Atributo requerido para precisar la cantidad de bienes o servicios del tipo particular definido por el presente concepto.
        :param clave_unidad: Atributo requerido para precisar la clave de unidad de medida estandarizada aplicable para la cantidad expresada en el concepto. La unidad debe corresponder con la descripción del concepto.
        :param descripcion: Atributo requerido para precisar la descripción del bien o servicio cubierto por el presente concepto.
        :param valor_unitario: Atributo requerido para precisar el valor o precio unitario del bien o servicio cubierto por el presente concepto.
        :param objeto_imp: Atributo requerido para expresar si la operación comercial es objeto o no de impuesto.
        :param no_identificacion: Atributo opcional para expresar el número de parte, identificador del producto o del servicio, la clave de producto o servicio, SKU o equivalente, propia de la operación del emisor, amparado por el presente concepto. Opcionalmente se puede utilizar claves del estándar GTIN.
        :param unidad: Atributo opcional para precisar la unidad de medida propia de la operación del emisor, aplicable para la cantidad expresada en el concepto. La unidad debe corresponder con la descripción del concepto.
        :param descuento: Atributo opcional para representar el importe de los descuentos aplicables al concepto. No se permiten valores negativos.
        :param a_cuenta_terceros: Nodo opcional para registrar información del contribuyente Tercero, a cuenta del que se realiza la operación.
        :param informacion_aduanera: Nodo opcional para introducir la información aduanera aplicable cuando se trate de ventas de primera mano de mercancías importadas o se trate de operaciones de comercio exterior con bienes o servicios.
        :param cuenta_predial: Nodo opcional para asentar el número de cuenta predial con el que fue registrado el inmueble, en el sistema catastral de la entidad federativa de que trate, o bien para incorporar los datos de identificación del certificado de participación inmobiliaria no amortizable.
        :param complemento_concepto: Nodo opcional donde se incluyen los nodos complementarios de extensión al concepto definidos por el SAT, de acuerdo con las disposiciones particulares para un sector o actividad específica.
        :param parte: Nodo opcional para expresar las partes o componentes que integran la totalidad del concepto expresado en el comprobante fiscal digital por Internet.
        :param traslados: Traslados a aplicar.
        :param retenciones: Retenciones a aplicar.
        :param _traslados_incluidos: si el valor valor_unitario ya incluye traslados.
        """

        super().__init__({
            'ClaveProdServ': clave_prod_serv,
            'Cantidad': cantidad,
            'ClaveUnidad': clave_unidad,
            'Descripcion': descripcion,
            'ValorUnitario': valor_unitario,
            'ObjetoImp': objeto_imp,
            'NoIdentificacion': no_identificacion,
            'Unidad': unidad,
            'Descuento': descuento,
            'ACuentaTerceros': a_cuenta_terceros,
            'InformacionAduanera': informacion_aduanera,
            'CuentaPredial': cuenta_predial,
            'ComplementoConcepto': complemento_concepto,
            'Parte': parte,
            'Impuestos': {
                'Traslados': traslados,
                'Retenciones': retenciones
            },
            '_traslados_incluidos': _traslados_incluidos
        })


class Receptor(XElement):
    """
    http://www.sat.gob.mx/cfd/4
    Nodo requerido para precisar la información del contribuyente receptor del comprobante.
    """

    def __init__(
            self,
            rfc: str,
            nombre: str,
            domicilio_fiscal_receptor: str,
            regimen_fiscal_receptor: str,
            uso_cfdi: str,
            residencia_fiscal: str = None,
            num_reg_id_trib: str = None,
    ):
        """
        Nodo requerido para precisar la información del contribuyente receptor del comprobante.

        :param rfc: Atributo requerido para registrar la Clave del Registro Federal de Contribuyentes correspondiente al contribuyente receptor del comprobante.
        :param nombre: Atributo requerido para registrar el nombre(s), primer apellido, segundo apellido, según corresponda, denominación o razón social del contribuyente, inscrito en el RFC, del receptor del comprobante.
        :param domicilio_fiscal_receptor: Atributo requerido para registrar el código postal del domicilio fiscal del receptor del comprobante.
        :param regimen_fiscal_receptor: Atributo requerido para incorporar la clave del régimen fiscal del contribuyente receptor al que aplicará el efecto fiscal de este comprobante.
        :param uso_cfdi: Atributo requerido para expresar la clave del uso que dará a esta factura el receptor del CFDI.
        :param residencia_fiscal: Atributo condicional para registrar la clave del país de residencia para efectos fiscales del receptor del comprobante, cuando se trate de un extranjero, y que es conforme con la especificación ISO 3166-1 alpha-3. Es requerido cuando se incluya el complemento de comercio exterior o se registre el atributo NumRegIdTrib.
        :param num_reg_id_trib: Atributo condicional para expresar el número de registro de identidad fiscal del receptor cuando sea residente en el extranjero. Es requerido cuando se incluya el complemento de comercio exterior.
        """

        super().__init__({
            'Rfc': rfc,
            'Nombre': nombre,
            'DomicilioFiscalReceptor': domicilio_fiscal_receptor,
            'RegimenFiscalReceptor': regimen_fiscal_receptor,
            'UsoCFDI': uso_cfdi,
            'ResidenciaFiscal': residencia_fiscal,
            'NumRegIdTrib': num_reg_id_trib,
        })


# MAIN #
class Comprobante(CFDI):
    """
    Estándar de Comprobante Fiscal Digital por Internet.
    """
    tag = '{http://www.sat.gob.mx/cfd/4}Comprobante'
    version = '4.0'
    complemento_pago = pago20.Pagos

    def __init__(
            self,
            emisor: Issuer,
            lugar_expedicion: str,
            receptor: Receptor | dict,
            conceptos: Concepto | Sequence[Concepto | dict],
            moneda: str = "MXN",
            tipo_de_comprobante: str = "I",
            exportacion: str = "01",
            serie: str = None,
            folio: str = None,
            forma_pago: str = None,
            condiciones_de_pago: str = None,
            tipo_cambio: Decimal | int = None,
            metodo_pago: str = None,
            confirmacion: str = None,
            informacion_global: InformacionGlobal | dict = None,
            cfdi_relacionados: CfdiRelacionados | Sequence[CfdiRelacionados | dict] = None,
            complemento: CFDI | Sequence[CFDI] = None,
            addenda: CFDI | Sequence[CFDI] = None,
            fecha: datetime = None,
    ):
        """
        Estándar de Comprobante Fiscal Digital por Internet.

        :param emisor: Nodo requerido para expresar la información del contribuyente emisor del comprobante.
        :param lugar_expedicion: Atributo requerido para incorporar el código postal del lugar de expedición del comprobante (domicilio de la matriz o de la sucursal).
        :param receptor: Nodo requerido para precisar la información del contribuyente receptor del comprobante.
        :param conceptos: Nodo requerido para listar los conceptos cubiertos por el comprobante.
        :param moneda: Atributo requerido para identificar la clave de la moneda utilizada para expresar los montos, cuando se usa moneda nacional se registra MXN. Conforme con la especificación ISO 4217.
        :param tipo_de_comprobante: Atributo requerido para expresar la clave del efecto del comprobante fiscal para el contribuyente emisor.
        :param exportacion: Atributo requerido para expresar si el comprobante ampara una operación de exportación.
        :param serie: Atributo opcional para precisar la serie para control interno del contribuyente. Este atributo acepta una cadena de caracteres.
        :param folio: Atributo opcional para control interno del contribuyente que expresa el folio del comprobante, acepta una cadena de caracteres.
        :param forma_pago: Atributo condicional para expresar la clave de la forma de pago de los bienes o servicios amparados por el comprobante.
        :param condiciones_de_pago: Atributo condicional para expresar las condiciones comerciales aplicables para el pago del comprobante fiscal digital por Internet. Este atributo puede ser condicionado mediante atributos o complementos.
        :param tipo_cambio: Atributo condicional para representar el tipo de cambio FIX conforme con la moneda usada. Es requerido cuando la clave de moneda es distinta de MXN y de XXX. El valor debe reflejar el número de pesos mexicanos que equivalen a una unidad de la divisa señalada en el atributo moneda. Si el valor está fuera del porcentaje aplicable a la moneda tomado del catálogo c_Moneda, el emisor debe obtener del PAC que vaya a timbrar el CFDI, de manera no automática, una clave de confirmación para ratificar que el valor es correcto e integrar dicha clave en el atributo Confirmacion.
        :param metodo_pago: Atributo condicional para precisar la clave del método de pago que aplica para este comprobante fiscal digital por Internet, conforme al Artículo 29-A fracción VII incisos a y b del CFF.
        :param confirmacion: Atributo condicional para registrar la clave de confirmación que entregue el PAC para expedir el comprobante con importes grandes, con un tipo de cambio fuera del rango establecido o con ambos casos. Es requerido cuando se registra un tipo de cambio o un total fuera del rango establecido.
        :param informacion_global: Nodo condicional para precisar la información relacionada con el comprobante global.
        :param cfdi_relacionados: Nodo opcional para precisar la información de los comprobantes relacionados.
        :param complemento: Nodo opcional donde se incluye el complemento Timbre Fiscal Digital de manera obligatoria y los nodos complementarios determinados por el SAT, de acuerdo con las disposiciones particulares para un sector o actividad específica.
        :param addenda: Nodo opcional para recibir las extensiones al presente formato que sean de utilidad al contribuyente. Para las reglas de uso del mismo, referirse al formato origen.
        :param fecha: Atributo requerido para la expresión de la fecha y hora de expedición del Comprobante Fiscal Digital por Internet. Se expresa en la forma AAAA-MM-DDThh:mm:ss y debe corresponder con la hora local donde se expide el comprobante.
        :return: objeto CFDI
        """

        rnd_fn = rounder(moneda)

        for concepto in iterate(conceptos):
            trasladados = [x if isinstance(x, Impuesto) else Impuesto.parse(x) for x in iterate(concepto.get("Impuestos", {}).get("Traslados"))]
            retenciones = [x if isinstance(x, Impuesto) else Impuesto.parse(x) for x in iterate(concepto.get("Impuestos", {}).get("Retenciones"))]

            if concepto.get('_traslados_incluidos'):
                s_tasa = sum(c["TasaOCuota"] for c in trasladados if c["TipoFactor"] == "Tasa")
                s_cuota = sum(c["TasaOCuota"] for c in trasladados if c["TipoFactor"] == "Cuota")
                if any(c for c in trasladados if c["TipoFactor"] in ('Tasa', 'Cuota') and (c.get('Base') is not None or c.get('Importe') is not None)):
                    raise ValueError("Not possible to compute '_traslados_incluidos' if any 'trasladados' contains 'Base' or 'Importe'")

                valor_unitario = concepto['ValorUnitario']
                valor_unitario = (valor_unitario - s_cuota) / (s_tasa + 1)
                concepto['ValorUnitario'] = rnd_fn(valor_unitario)
            else:
                valor_unitario = concepto['ValorUnitario']

            importe = concepto["Cantidad"] * valor_unitario
            concepto["Importe"] = rnd_fn(importe)

            if concepto.get("ObjetoImp") in ("01", "03"):
                concepto['Impuestos'] = None
                continue

            base = importe - (concepto.get("Descuento") or 0)

            impuestos = {
                imp_t: [
                    make_impuesto(i, base=base, rnd_fn=rnd_fn) for i in imp
                ]
                for imp_t, imp in [('Traslados', trasladados), ('Retenciones', retenciones)] if imp
            }

            concepto['Impuestos'] = impuestos or None
            concepto["ObjetoImp"] = "02" if impuestos else "01"

        sub_total = sum(c['Importe'] for c in iterate(conceptos))
        descuento = sum(c.get('Descuento') or 0 for c in iterate(conceptos))
        impuestos = make_impuestos(conceptos)

        total = sub_total - descuento
        if impuestos:
            total += impuestos.get('TotalImpuestosTrasladados', 0)
            total -= impuestos.get('TotalImpuestosRetenidos', 0)

        descuento = descuento or None
        fecha = fecha or datetime.now(tz=get_timezone(lugar_expedicion)).replace(tzinfo=None)

        super().__init__({
            'Version': self.version,
            'Fecha': fecha,
            'NoCertificado': emisor.certificate_number,
            'Certificado': emisor.signer.certificate_base64() if emisor.signer else '',
            'Sello': '',
            'SubTotal': sub_total,
            'Moneda': moneda,
            'Total': total,
            'TipoDeComprobante': tipo_de_comprobante,
            'Exportacion': exportacion,
            'LugarExpedicion': lugar_expedicion,
            'Serie': serie,
            'Folio': folio,
            'FormaPago': forma_pago,
            'CondicionesDePago': condiciones_de_pago,
            'Descuento': descuento,
            'TipoCambio': tipo_cambio,
            'MetodoPago': metodo_pago,
            'Confirmacion': confirmacion,
            'InformacionGlobal': informacion_global,
            'CfdiRelacionados': cfdi_relacionados,
            'Emisor': {
                "Rfc": emisor.rfc,
                "Nombre": emisor.legal_name,
                "RegimenFiscal": emisor.tax_system
            },
            'Receptor': receptor,
            'Conceptos': conceptos,
            'Impuestos': impuestos,
            'Complemento': complemento,
            'Addenda': addenda,
        })
        if emisor.signer:
            self['Sello'] = emisor.signer.sign_sha256(
                self.cadena_original().encode()
            )

    @classmethod
    def pago(
            cls,
            emisor: Issuer,
            lugar_expedicion: str,
            receptor: Receptor | dict,
            complemento_pago: CFDI,
            cfdi_relacionados: CfdiRelacionados | Sequence[CfdiRelacionados | dict] = None,
            confirmacion: str = None,
            serie: str = None,
            folio: str = None,
            addenda: CFDI | Sequence[CFDI] = None,
            fecha: datetime = None) -> CFDI:
        """
        Estándar de Comprobante Fiscal Digital por Internet de Tipo Pago.

        :param emisor: Nodo requerido para expresar la información del contribuyente emisor del comprobante.
        :param lugar_expedicion: Atributo requerido para incorporar el código postal del lugar de expedición del comprobante (domicilio de la matriz o de la sucursal).
        :param receptor: Nodo requerido para precisar la información del contribuyente receptor del comprobante.
        :param complemento_pago: Pago
        :param serie: Atributo opcional para precisar la serie para control interno del contribuyente. Este atributo acepta una cadena de caracteres.
        :param folio: Atributo opcional para control interno del contribuyente que expresa el folio del comprobante, acepta una cadena de caracteres.
        :param confirmacion: Atributo condicional para registrar la clave de confirmación que entregue el PAC para expedir el comprobante con importes grandes, con un tipo de cambio fuera del rango establecido o con ambos casos. Es requerido cuando se registra un tipo de cambio o un total fuera del rango establecido.
        :param cfdi_relacionados: Nodo opcional para precisar la información de los comprobantes relacionados.
        :param addenda: Nodo opcional para recibir las extensiones al presente formato que sean de utilidad al contribuyente. Para las reglas de uso del mismo, referirse al formato origen.
        :param fecha: Atributo requerido para la expresión de la fecha y hora de expedición del Comprobante Fiscal Digital por Internet. Se expresa en la forma AAAA-MM-DDThh:mm:ss y debe corresponder con la hora local donde se expide el comprobante.
        :return: objeto CFDI
        """
        if cls.version == "3.3":
            receptor["UsoCFDI"] = "P01"
        else:
            receptor["UsoCFDI"] = "CP01"

        return cls(
            emisor=emisor,
            lugar_expedicion=lugar_expedicion,
            receptor=receptor,
            conceptos=Concepto(
                clave_prod_serv='84111506',
                cantidad=1,
                clave_unidad='ACT',
                descripcion='Pago',
                valor_unitario=Decimal(0),
                objeto_imp="01"
            ),
            complemento=complemento_pago,
            serie=serie,
            folio=folio,
            moneda='XXX',
            tipo_de_comprobante='P',
            cfdi_relacionados=cfdi_relacionados,
            confirmacion=confirmacion,
            exportacion="01",
            addenda=addenda,
            fecha=fecha
        )

    @classmethod
    def pago_comprobante(
            cls,
            emisor: Issuer,
            lugar_expedicion: str,
            comprobante: CFDI,
            num_parcialidad: int,
            imp_saldo_ant: Decimal | int,
            imp_pagado: Decimal | int,
            fecha_pago: datetime,
            forma_pago: str,
            tipo_cambio: Decimal | int = None,
            cfdi_relacionados: CfdiRelacionados | Sequence[CfdiRelacionados | dict] = None,
            confirmacion: str = None,
            serie: str = None,
            folio: str = None,
            addenda: CFDI | Sequence[CFDI] = None,
            fecha: datetime = None) -> CFDI:
        """
        Estándar de Comprobante Fiscal Digital por Internet de Tipo Pago. Generado a partir de un Comprobante

        :param emisor: Nodo requerido para expresar la información del contribuyente emisor del comprobante.
        :param lugar_expedicion: Atributo requerido para incorporar el código postal del lugar de expedición del comprobante (domicilio de la matriz o de la sucursal).
        :param comprobante: CFDIS de Comprobante de Ingreso para generar el pago por su monto total
        :param num_parcialidad: Atributo requerido para expresar el número de parcialidad que corresponde al pago.
        :param imp_saldo_ant: Atributo requerido para expresar el monto del saldo insoluto de la parcialidad anterior. En el caso de que sea la primer parcialidad este atributo debe contener el importe total del documento relacionado.
        :param imp_pagado: Atributo requerido para expresar el importe pagado para el documento relacionado.
        :param fecha_pago: Atributo requerido para expresar la fecha y hora en la que el beneficiario recibe el pago. Se expresa en la forma aaaa-mm-ddThh:mm:ss, de acuerdo con la especificación ISO 8601.En caso de no contar con la hora se debe registrar 12:00:00.
        :param serie: Atributo opcional para precisar la serie para control interno del contribuyente. Este atributo acepta una cadena de caracteres.
        :param folio: Atributo opcional para control interno del contribuyente que expresa el folio del comprobante, acepta una cadena de caracteres.
        :param forma_pago: Atributo condicional para expresar la clave de la forma de pago de los bienes o servicios amparados por el comprobante.
        :param tipo_cambio: Atributo condicional para representar el tipo de cambio FIX conforme con la moneda usada. Es requerido cuando la clave de moneda es distinta de MXN y de XXX. El valor debe reflejar el número de pesos mexicanos que equivalen a una unidad de la divisa señalada en el atributo moneda. Si el valor está fuera del porcentaje aplicable a la moneda tomado del catálogo c_Moneda, el emisor debe obtener del PAC que vaya a timbrar el CFDI, de manera no automática, una clave de confirmación para ratificar que el valor es correcto e integrar dicha clave en el atributo Confirmacion.
        :param confirmacion: Atributo condicional para registrar la clave de confirmación que entregue el PAC para expedir el comprobante con importes grandes, con un tipo de cambio fuera del rango establecido o con ambos casos. Es requerido cuando se registra un tipo de cambio o un total fuera del rango establecido.
        :param cfdi_relacionados: Nodo opcional para precisar la información de los comprobantes relacionados.
        :param addenda: Nodo opcional para recibir las extensiones al presente formato que sean de utilidad al contribuyente. Para las reglas de uso del mismo, referirse al formato origen.
        :param fecha: Atributo requerido para la expresión de la fecha y hora de expedición del Comprobante Fiscal Digital por Internet. Se expresa en la forma AAAA-MM-DDThh:mm:ss y debe corresponder con la hora local donde se expide el comprobante.
        :return: objeto CFDI
        """
        first_cfdi = comprobante
        moneda = first_cfdi['Moneda']
        receptor = first_cfdi['Receptor'].copy()

        # CRP204: El campo TipoCambioP no debe estar presente cuando el campo Moneda contenga ^MXN$ en el nodo Pago
        if cls.complemento_pago.version == "1.0":
            if moneda == 'MXN' and tipo_cambio == 1:
                tipo_cambio = None
        else:
            if moneda == 'MXN' and tipo_cambio is None:
                tipo_cambio = 1

        c = comprobante
        if not c["Moneda"] == moneda:
            raise ValueError("Moneda de comprobante es diferente de Moneda de Pago")

        return cls.pago(
            emisor=emisor,
            lugar_expedicion=lugar_expedicion,
            receptor=receptor,
            complemento_pago=cls.complemento_pago(
                pago=[
                    {
                        'DoctoRelacionado': [
                            {
                                'IdDocumento': c["Complemento"]["TimbreFiscalDigital"]["UUID"],
                                'Serie': c.get("Serie"),
                                'Folio': c.get("Folio"),
                                'MonedaDR': c["Moneda"],
                                'EquivalenciaDR': 1,
                                'MetodoDePagoDR': c["MetodoPago"],
                                'NumParcialidad': num_parcialidad,
                                'ImpSaldoAnt': imp_saldo_ant,
                                'ImpPagado': imp_pagado,
                                'ObjetoImpDR': '02' if 'Impuestos' in c else '01',
                                'ImpuestosDR': make_impuestos_dr_parcial(
                                    conceptos=c['Conceptos'],
                                    imp_saldo_ant=imp_saldo_ant,
                                    imp_pagado=imp_pagado,
                                    total=c["Total"],
                                    rnd_fn=rounder(c["Moneda"])
                                ) if 'Impuestos' in c else None
                            }
                        ],
                        'FechaPago': fecha_pago,
                        'FormaDePagoP': forma_pago,
                        'MonedaP': moneda,
                        'TipoCambioP': tipo_cambio
                    }
                ]
            ),
            cfdi_relacionados=cfdi_relacionados,
            confirmacion=confirmacion,
            serie=serie,
            folio=folio,
            addenda=addenda,
            fecha=fecha
        )

    @classmethod
    def pago_comprobantes(
            cls,
            emisor: Issuer,
            lugar_expedicion: str,
            comprobantes: Sequence[CFDI],
            fecha_pago: datetime,
            forma_pago: str,
            tipo_cambio: Decimal | int = None,
            cfdi_relacionados: CfdiRelacionados | Sequence[CfdiRelacionados | dict] = None,
            confirmacion: str = None,
            serie: str = None,
            folio: str = None,
            addenda: CFDI | Sequence[CFDI] = None,
            fecha: datetime = None) -> CFDI:
        """
        Estándar de Comprobante Fiscal Digital por Internet de Tipo Pago. Generado a partir de una lista de Comprobantes
        Se asume que los comprobantes se pagan en su totalidad en una sola exhibición

        :param emisor: Nodo requerido para expresar la información del contribuyente emisor del comprobante.
        :param lugar_expedicion: Atributo requerido para incorporar el código postal del lugar de expedición del comprobante (domicilio de la matriz o de la sucursal).
        :param comprobantes: Sequence[Mapping[str, Any]]a de CFDIS de Comprobante de Ingreso para generar el pago por su monto total
        :param fecha_pago: Atributo requerido para expresar la fecha y hora en la que el beneficiario recibe el pago. Se expresa en la forma aaaa-mm-ddThh:mm:ss, de acuerdo con la especificación ISO 8601.En caso de no contar con la hora se debe registrar 12:00:00.
        :param serie: Atributo opcional para precisar la serie para control interno del contribuyente. Este atributo acepta una cadena de caracteres.
        :param folio: Atributo opcional para control interno del contribuyente que expresa el folio del comprobante, acepta una cadena de caracteres.
        :param forma_pago: Atributo condicional para expresar la clave de la forma de pago de los bienes o servicios amparados por el comprobante.
        :param tipo_cambio: Atributo condicional para representar el tipo de cambio FIX conforme con la moneda usada. Es requerido cuando la clave de moneda es distinta de MXN y de XXX. El valor debe reflejar el número de pesos mexicanos que equivalen a una unidad de la divisa señalada en el atributo moneda. Si el valor está fuera del porcentaje aplicable a la moneda tomado del catálogo c_Moneda, el emisor debe obtener del PAC que vaya a timbrar el CFDI, de manera no automática, una clave de confirmación para ratificar que el valor es correcto e integrar dicha clave en el atributo Confirmacion.
        :param confirmacion: Atributo condicional para registrar la clave de confirmación que entregue el PAC para expedir el comprobante con importes grandes, con un tipo de cambio fuera del rango establecido o con ambos casos. Es requerido cuando se registra un tipo de cambio o un total fuera del rango establecido.
        :param cfdi_relacionados: Nodo opcional para precisar la información de los comprobantes relacionados.
        :param addenda: Nodo opcional para recibir las extensiones al presente formato que sean de utilidad al contribuyente. Para las reglas de uso del mismo, referirse al formato origen.
        :param fecha: Atributo requerido para la expresión de la fecha y hora de expedición del Comprobante Fiscal Digital por Internet. Se expresa en la forma AAAA-MM-DDThh:mm:ss y debe corresponder con la hora local donde se expide el comprobante.
        :return: objeto CFDI
        """
        first_cfdi = comprobantes[0]
        moneda = first_cfdi['Moneda']
        receptor = first_cfdi['Receptor'].copy()

        # CRP204: El campo TipoCambioP no debe estar presente cuando el campo Moneda contenga ^MXN$ en el nodo Pago
        if cls.complemento_pago.version == "1.0":
            if moneda == 'MXN' and tipo_cambio == 1:
                tipo_cambio = None
        else:
            if moneda == 'MXN' and tipo_cambio is None:
                tipo_cambio = 1

        if not all(
                c["Moneda"] == moneda
                and c["Emisor"]["Rfc"] == emisor.rfc
                and c["Emisor"]["RegimenFiscal"] == emisor.tax_system
                and c["Receptor"]["Rfc"] == receptor["Rfc"]
                and c["Receptor"].get("RegimenFiscalReceptor") == receptor.get("RegimenFiscalReceptor")
                for c in comprobantes
        ):
            raise ValueError("CFDIS are of different RFC's Emisor/Receptor o Moneda")

        return cls.pago(
            emisor=emisor,
            lugar_expedicion=lugar_expedicion,
            receptor=receptor,
            complemento_pago=cls.complemento_pago(
                pago=[
                    {
                        'DoctoRelacionado': [
                            {
                                'IdDocumento': c["Complemento"]["TimbreFiscalDigital"]["UUID"],
                                'Serie': c.get("Serie"),
                                'Folio': c.get("Folio"),
                                'MonedaDR': c["Moneda"],
                                'EquivalenciaDR': 1,
                                'MetodoDePagoDR': c["MetodoPago"],
                                'NumParcialidad': 1,
                                'ImpSaldoAnt': c["Total"],
                                'ImpPagado': c["Total"],
                                'ObjetoImpDR': '02' if 'Impuestos' in c else '01',
                                'ImpuestosDR': make_impuestos_dr(c['Conceptos']) if 'Impuestos' in c else None
                            } for c in comprobantes
                        ],
                        'FechaPago': fecha_pago,
                        'FormaDePagoP': forma_pago,
                        'MonedaP': moneda,
                        'TipoCambioP': tipo_cambio
                    }
                ]
            ),
            cfdi_relacionados=cfdi_relacionados,
            confirmacion=confirmacion,
            serie=serie,
            folio=folio,
            addenda=addenda,
            fecha=fecha
        )

    @classmethod
    def nomina(
            cls,
            emisor: Issuer,
            lugar_expedicion: str,
            receptor: Receptor | dict,
            complemento_nomina: CFDI,
            cfdi_relacionados: CfdiRelacionados | Sequence[CfdiRelacionados | dict] = None,
            confirmacion: str = None,
            serie: str = None,
            folio: str = None,
            addenda: CFDI | Sequence[CFDI] = None,
            fecha: datetime = None) -> CFDI:
        """
        Estándar de Comprobante Fiscal Digital por Internet de Tipo Pago.

        :param emisor: Nodo requerido para expresar la información del contribuyente emisor del comprobante.
        :param lugar_expedicion: Atributo requerido para incorporar el código postal del lugar de expedición del comprobante (domicilio de la matriz o de la sucursal).
        :param receptor: Nodo requerido para precisar la información del contribuyente receptor del comprobante.
        :param complemento_nomina: Pago
        :param serie: Atributo opcional para precisar la serie para control interno del contribuyente. Este atributo acepta una cadena de caracteres.
        :param folio: Atributo opcional para control interno del contribuyente que expresa el folio del comprobante, acepta una cadena de caracteres.
        :param confirmacion: Atributo condicional para registrar la clave de confirmación que entregue el PAC para expedir el comprobante con importes grandes, con un tipo de cambio fuera del rango establecido o con ambos casos. Es requerido cuando se registra un tipo de cambio o un total fuera del rango establecido.
        :param cfdi_relacionados: Nodo opcional para precisar la información de los comprobantes relacionados.
        :param addenda: Nodo opcional para recibir las extensiones al presente formato que sean de utilidad al contribuyente. Para las reglas de uso del mismo, referirse al formato origen.
        :param fecha: Atributo requerido para la expresión de la fecha y hora de expedición del Comprobante Fiscal Digital por Internet. Se expresa en la forma AAAA-MM-DDThh:mm:ss y debe corresponder con la hora local donde se expide el comprobante.
        :return: objeto CFDI
        """
        if cls.version == "3.3":
            receptor["UsoCFDI"] = "P01"
        else:
            receptor["UsoCFDI"] = "CN01"

        concepto = Concepto(
            clave_prod_serv='84111505',
            cantidad=1,
            clave_unidad='ACT',
            descripcion='Pago de nómina',
            valor_unitario=complemento_nomina.get('TotalPercepciones', 0) + complemento_nomina.get('TotalOtrosPagos', 0),
            descuento=complemento_nomina.get('TotalDeducciones'),
            objeto_imp="03"
        )
        return cls(
            emisor=emisor,
            lugar_expedicion=lugar_expedicion,
            receptor=receptor,
            conceptos=concepto,
            complemento=complemento_nomina,
            serie=serie,
            folio=folio,
            moneda='MXN',
            tipo_de_comprobante='N',
            metodo_pago="PUE",
            forma_pago="99",
            cfdi_relacionados=cfdi_relacionados,
            confirmacion=confirmacion,
            exportacion="01",
            addenda=addenda,
            fecha=fecha,
        )