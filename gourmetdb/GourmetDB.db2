CREATE TABLE GOURMET.TIENDA  (
                  NOMBRE CHAR(100) NOT NULL ,
                  DIRECCION CHAR(100) NOT NULL ,
                  SUPERFICIE DECIMAL(5,2) NOT NULL ,
                  FORMATO_TIENDA CHAR(100) NOT NULL ,
                  PAIS CHAR(100) NOT NULL ,
                  TIPO_ZONA CHAR(100) NOT NULL )
                 IN USERSPACE1 ;

import from tienda.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.tienda;

-- DDL Statements for primary key on Table GOURMET.TIENDA

ALTER TABLE GOURMET.TIENDA
        ADD CONSTRAINT CC1187120357877 PRIMARY KEY
                (NOMBRE);

------------------------------------------------
-- DDL Statements for table GOURMET.PAIS
------------------------------------------------


CREATE TABLE GOURMET.PAIS  (
                  NOMBREPAIS CHAR(100) NOT NULL ,
                  EXTENSION DECIMAL(10,0) NOT NULL ,
                  POBLACION DECIMAL(10,0) NOT NULL ,
                  NOMBREREGION CHAR(100) NOT NULL )
                 IN USERSPACE1 ;

import from pais.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.pais;

-- DDL Statements for primary key on Table GOURMET.PAIS

ALTER TABLE GOURMET.PAIS
        ADD CONSTRAINT CC1186736972792 PRIMARY KEY
                (NOMBREPAIS);

------------------------------------------------
-- DDL Statements for table GOURMET.REGIONGEOGRAFICA
------------------------------------------------


CREATE TABLE GOURMET.REGIONGEOGRAFICA  (
                  NOMBREREGION CHAR(100) NOT NULL ,
                  CONTINENTE CHAR(100) NOT NULL )
                 IN USERSPACE1 ;

import from regiongeografica.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.regiongeografica;

ALTER TABLE GOURMET.REGIONGEOGRAFICA
        ADD CONSTRAINT CC1186758129270 PRIMARY KEY
                (NOMBREREGION);

CREATE TABLE GOURMET.CLIENTE  (
                  CODCLIENTE CHAR(10) NOT NULL ,
                  NOMBRECLIENTE CHAR(100) ,
                  SEXO CHAR(25) ,
                  FECHANACIMIENTO DATE ,
                  ESTADOCIVIL CHAR(25) ,
                  DIRECCIÓN CHAR(100) ,
                  PROFESIÓN CHAR(100) ,
                  NUMEROHIJOS INTEGER ,
                  REGION CHAR(100) ,
                  NACIONALIDAD CHAR(100) ,
                  TOTALCOMPRAS INTEGER ,
                  PUNTOSACUMULADOS INTEGER )
                 IN USERSPACE1 ;

import from cliente.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.cliente;

-- DDL Statements for primary key on Table GOURMET.CLIENTE

ALTER TABLE GOURMET.CLIENTE
        ADD CONSTRAINT CC1186758966594 PRIMARY KEY
                (CODCLIENTE);

------------------------------------------------
-- DDL Statements for table GOURMET.PRODUCTO
------------------------------------------------


CREATE TABLE GOURMET.PRODUCTO  (
                  CODPRODUCTO CHAR(25) NOT NULL ,
                  DESCRIPCIÓN CHAR(100) NOT NULL ,
                  NOMBREPAIS CHAR(100) NOT NULL ,
                  COSTE DECIMAL(5,2) NOT NULL ,
                  PRECIOVENTA DECIMAL(5,2) NOT NULL ,
                  TIPOUNIDAD CHAR(100) NOT NULL ,
                  NOMBRESUBFAMILIA CHAR(100) NOT NULL ,
                  MARCA CHAR(100) NOT NULL ,
                  CODPROVEEDOR CHAR(10) NOT NULL )
                 IN USERSPACE1 ;

import from producto.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.producto;

-- DDL Statements for primary key on Table GOURMET.PRODUCTO

ALTER TABLE GOURMET.PRODUCTO
        ADD CONSTRAINT CC1187115240218 PRIMARY KEY
                (CODPRODUCTO);

------------------------------------------------
-- DDL Statements for table GOURMET.PROVEEDOR
------------------------------------------------


CREATE TABLE GOURMET.PROVEEDOR  (
                  CODPROVEEDOR CHAR(10) NOT NULL ,
                  NOMBREPROVEEDOR CHAR(100) NOT NULL ,
                  PERSONACONTACTO CHAR(100) NOT NULL ,
                  DIRECCIÓN CHAR(100) NOT NULL ,
                  TELÉFONO CHAR(25) NOT NULL ,
                  PERIODOPAGO SMALLINT ,
                  PAGOPENDIENTE DECIMAL(5,2) ,
                  TIPOPROVEEDOR CHAR(100) ,
                  ALCANCE CHAR(25) NOT NULL )
                 IN USERSPACE1 ;

import from proveedor.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.proveedor;

-- DDL Statements for primary key on Table GOURMET.PROVEEDOR

ALTER TABLE GOURMET.PROVEEDOR
        ADD CONSTRAINT CC1187115755870 PRIMARY KEY
                (CODPROVEEDOR);

------------------------------------------------
-- DDL Statements for table GOURMET.NOMBRESUBFAMILIA
------------------------------------------------


CREATE TABLE GOURMET.NOMBRESUBFAMILIA  (
                  NOMBRESUBFAMILIA CHAR(100) NOT NULL ,
                  DESCRIPCIÓN CHAR(100) ,
                  NOMBREFAMILIA CHAR(100) NOT NULL )
                 IN USERSPACE1 ;

import from subfamilia.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.nombresubfamilia;

-- DDL Statements for primary key on Table GOURMET.NOMBRESUBFAMILIA

ALTER TABLE GOURMET.NOMBRESUBFAMILIA
        ADD CONSTRAINT CC1187116579834 PRIMARY KEY
                (NOMBRESUBFAMILIA);

------------------------------------------------
-- DDL Statements for table GOURMET.FAMILIA
------------------------------------------------


CREATE TABLE GOURMET.FAMILIA  (
                  NOMBREFAMILIA CHAR(100) NOT NULL ,
                  DESCRIPCIÓN CHAR(100) ,
                  NOMBRESECCIÓN CHAR(100) NOT NULL )
                 IN USERSPACE1 ;

import from familia.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.familia;

-- DDL Statements for primary key on Table GOURMET.FAMILIA

ALTER TABLE GOURMET.FAMILIA
        ADD CONSTRAINT CC1187116923569 PRIMARY KEY
                (NOMBREFAMILIA);

------------------------------------------------
-- DDL Statements for table GOURMET.SECCION
------------------------------------------------


CREATE TABLE GOURMET.SECCION  (
                  NOMBRESECCIÓN CHAR(100) NOT NULL ,
                  DESCRIPCIÓN CHAR(100) )
                 IN USERSPACE1 ;

import from seccion.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.seccion;

-- DDL Statements for primary key on Table GOURMET.SECCION

ALTER TABLE GOURMET.SECCION
        ADD CONSTRAINT CC1187117338345 PRIMARY KEY
                (NOMBRESECCIÓN);

------------------------------------------------
-- DDL Statements for table GOURMET.CABECERATICKET
------------------------------------------------


CREATE TABLE GOURMET.CABECERATICKET  (
                  CODVENTA CHAR(25) NOT NULL ,
                  NOMBRETIENDA CHAR(100) NOT NULL ,
                  FECHA DATE NOT NULL ,
                  HORA SMALLINT NOT NULL ,
                  FORMAPAGO CHAR(100) NOT NULL ,
                  CODCLIENTE CHAR(25) ,
                  IMPORTETOTAL DECIMAL(8,4) NOT NULL ,
                  TOTALUNIDADES SMALLINT NOT NULL ,
                  PUNTOSTICKET SMALLINT NOT NULL )
                 IN USERSPACE1 ;

import from cabeceraticket.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.cabeceraticket;

-- DDL Statements for primary key on Table GOURMET.CABECERATICKET

ALTER TABLE GOURMET.CABECERATICKET
        ADD CONSTRAINT CC1187118498213 PRIMARY KEY
                (CODVENTA);

------------------------------------------------
-- DDL Statements for table GOURMET.LINEASTICKET
------------------------------------------------


CREATE TABLE GOURMET.LINEASTICKET  (
                  CODLINEA SMALLINT NOT NULL ,
                  CODVENTA CHAR(25) NOT NULL ,
                  NOMBRETIENDA CHAR(100) NOT NULL ,
                  CODPRODUCTO CHAR(100) NOT NULL ,
                  CANTIDAD SMALLINT NOT NULL ,
                  PRECIOVENTA DECIMAL(8,4) NOT NULL ,
                  NOMBREPROMOCION CHAR(100) ,
                  CODCABECERA INTEGER NOT NULL )
                 IN USERSPACE1 ;

import from lineasticket.cvs
of del modified by CHARDEL""  COLDEL, DECPT. COMMITCOUNT 500
insert into gourmet.lineasticket;

------------------------------------------------
-- DDL Statements for table GOURMET.PROMOCION
------------------------------------------------


CREATE TABLE GOURMET.PROMOCION  (
                  NOMBREPROMOCION CHAR(100) NOT NULL ,
                  TIPOPROMOCION CHAR(100) NOT NULL ,
                  COSTE SMALLINT ,
                  FECHAINICIO DATE NOT NULL ,
                  FECHAFIN DATE NOT NULL ,
                  CODPRODUCTO CHAR(25) NOT NULL ,
                  NOMBREFAMILIA CHAR(25) ,
                  NOMBRESECCIÓN CHAR(25) ,
                  NOMBRETIENDA CHAR(25) ,
                  NOMBREREGION CHAR(25) ,
                  NOMBREPAIS CHAR(25) )
                 IN USERSPACE1 ;

import from promocion.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.promocion;

-- DDL Statements for primary key on Table GOURMET.PROMOCION

ALTER TABLE GOURMET.PROMOCION
        ADD CONSTRAINT CC1187123330592 PRIMARY KEY
                (NOMBREPROMOCION);

------------------------------------------------
-- DDL Statements for table GOURMET.PEDIDO
------------------------------------------------


CREATE TABLE GOURMET.PEDIDO  (
                  CODPEDIDO CHAR(25) NOT NULL ,
                  NOMBRETIENDA CHAR(25) NOT NULL ,
                  CODPRODUCTO CHAR(25) NOT NULL ,
                  PRECIOCOMPRA DECIMAL(8,4) NOT NULL ,
                  CANTIDADSOLICITADA SMALLINT NOT NULL ,
                  FECHASOLICITUD DATE NOT NULL ,
                  CANTIDADENTREGADA SMALLINT NOT NULL ,
                  FECHAENTREGA DATE NOT NULL )
                 IN USERSPACE1 ;

import from pedido.cvs
of del modified by CHARDEL""  COLDEL, DECPT.
insert into gourmet.pedido;

-- DDL Statements for primary key on Table GOURMET.PEDIDO

ALTER TABLE GOURMET.PEDIDO
        ADD CONSTRAINT CC1187124047993 PRIMARY KEY
                (CODPEDIDO);

-- DDL Statements for foreign keys on Table GOURMET.TIENDA

ALTER TABLE GOURMET.TIENDA
        ADD CONSTRAINT CC1186736993542 FOREIGN KEY
                (PAIS)
        REFERENCES GOURMET.PAIS
                (NOMBREPAIS)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

-- DDL Statements for foreign keys on Table GOURMET.PAIS

ALTER TABLE GOURMET.PAIS
        ADD CONSTRAINT CC1186758418396 FOREIGN KEY
                (NOMBREREGION)
        REFERENCES GOURMET.REGIONGEOGRAFICA
                (NOMBREREGION)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

-- DDL Statements for foreign keys on Table GOURMET.PRODUCTO

ALTER TABLE GOURMET.PRODUCTO
        ADD CONSTRAINT CC1187116214319 FOREIGN KEY
                (CODPROVEEDOR)
        REFERENCES GOURMET.PROVEEDOR
                (CODPROVEEDOR)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

ALTER TABLE GOURMET.PRODUCTO
        ADD CONSTRAINT CC1187116736740 FOREIGN KEY
                (NOMBRESUBFAMILIA)
        REFERENCES GOURMET.NOMBRESUBFAMILIA
                (NOMBRESUBFAMILIA)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

-- DDL Statements for foreign keys on Table GOURMET.NOMBRESUBFAMILIA

ALTER TABLE GOURMET.NOMBRESUBFAMILIA
        ADD CONSTRAINT CC1187117079994 FOREIGN KEY
                (NOMBREFAMILIA)
        REFERENCES GOURMET.FAMILIA
                (NOMBREFAMILIA)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

-- DDL Statements for foreign keys on Table GOURMET.FAMILIA

ALTER TABLE GOURMET.FAMILIA
        ADD CONSTRAINT CC1187117465508 FOREIGN KEY
                (NOMBRESECCIÓN)
        REFERENCES GOURMET.SECCION
                (NOMBRESECCIÓN)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

-- DDL Statements for foreign keys on Table GOURMET.CABECERATICKET

ALTER TABLE GOURMET.CABECERATICKET
        ADD CONSTRAINT CC1187120408780 FOREIGN KEY
                (NOMBRETIENDA)
        REFERENCES GOURMET.TIENDA
                (NOMBRE)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

ALTER TABLE GOURMET.CABECERATICKET
        ADD CONSTRAINT CC1187120454616 FOREIGN KEY
                (CODCLIENTE)
        REFERENCES GOURMET.CLIENTE
                (CODCLIENTE)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

-- DDL Statements for foreign keys on Table GOURMET.LINEASTICKET

ALTER TABLE GOURMET.LINEASTICKET
        ADD CONSTRAINT CC1187122110327 FOREIGN KEY
                (CODPRODUCTO)
        REFERENCES GOURMET.PRODUCTO
                (CODPRODUCTO)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

ALTER TABLE GOURMET.LINEASTICKET
        ADD CONSTRAINT CC1187122504604 FOREIGN KEY
                (CODVENTA)
        REFERENCES GOURMET.CABECERATICKET
                (CODVENTA)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

ALTER TABLE GOURMET.LINEASTICKET
        ADD CONSTRAINT CC1187123511161 FOREIGN KEY
                (NOMBREPROMOCION)
        REFERENCES GOURMET.PROMOCION
                (NOMBREPROMOCION)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

-- DDL Statements for foreign keys on Table GOURMET.PEDIDO

ALTER TABLE GOURMET.PEDIDO
        ADD CONSTRAINT CC1187124191039 FOREIGN KEY
                (NOMBRETIENDA)
        REFERENCES GOURMET.TIENDA
                (NOMBRE)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

ALTER TABLE GOURMET.PEDIDO
        ADD CONSTRAINT CC1187124235913 FOREIGN KEY
                (CODPRODUCTO)
        REFERENCES GOURMET.PRODUCTO
                (CODPRODUCTO)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
        ENFORCED
        ENABLE QUERY OPTIMIZATION;

COMMIT WORK;

CONNECT RESET;

TERMINATE;
------------------------------------------------
-- DDL Statements for table GOURMET.CLI
