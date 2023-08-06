from OpenSSL import crypto, SSL
import os, sys


def generateKey(cuit:int,bits:int=2048,type_pk=crypto.TYPE_RSA,save_file=False):
    """ Funcion para generar una private key con python

    :param cuit: CUIT a generar la PK
    :type cuit: int
    :param bits: Bits de la clave privada (2048 por default)
    :type bits: int
    :param type_pk: tipo de clave, por default TYPE_RSA
    :type type_pk: crypto Type
    :param save_file: si se desea guardar la clave en un archivo, False por default
    :type save_file: boolean
    :return: key
    :rtype: Key de PyOpenSSL

    """

    key = crypto.PKey()
    key.generate_key(type_pk, bits)
    if save_file:
        keyfile = 'pk_' + str(cuit) + '.key'
        f = open(keyfile, "wb")
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        f.close()

    return key

def generateCSR(cuit:int,razon_social:str,key,save_file=False):
    """ Funcion para generar el CSR

    :param cuit: CUIT a generar la PK
    :type cuit: int
    :param razon_social: Razon social del facturante
    :type razon_social: str
    :param save_file: si se desea guardar el certificado en un archivo, False por default
    :type save_file: boolean
    :return: CSR
    :rtype: string

    """
    req = crypto.X509Req()
    # Return an X509Name object representing the subject of the certificate.
    req.get_subject().CN = 'muvi_facturacion'
    req.get_subject().C = 'AR'
    req.get_subject().O = razon_social
    req.get_subject().serialNumber = 'CUIT '+str(cuit)
    req.set_pubkey(key)
    # Sign the certificate, using the key pkey and the message digest algorithm identified by the string digest.
    req.sign(key, "sha1")
    # Dump the certificate request req into a buffer string encoded with the type type.
    CSR = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
    if save_file:
        csrfile = f'cert_{str(cuit)}.csr'
        f = open(csrfile, "wb")
        f.write(CSR)
        f.close()
    return CSR.decode('utf-8')