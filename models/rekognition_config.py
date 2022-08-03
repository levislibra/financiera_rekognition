# -*- coding: utf-8 -*-

from openerp import models, fields, api

class FinancieraRekognitionConfig(models.Model):
	_name = 'financiera.rekognition.config'

	name = fields.Char('Nombre')
	id_access_key = fields.Char("ID de acceso")
	secret_access_key = fields.Char("Clave de acceso")
	region = fields.Char("Region")
	# dni frontal
	check_idcards_document_passport = fields.Boolean('Requerir etiqueta Id Cards|Document|Passport')
	check_idcards_document_passport_confidence = fields.Float('Confianza', help='De 0 a 100')
	check_idcards_document_passport_minimal_bounding = fields.Char('Cuadro delimitador (T,L,W,H)', default='0.0,0.0,0.0,0.0')
	check_person_human = fields.Boolean('Requerir etiqueta Person|Human')
	check_person_human_confidence = fields.Float('Confianza')
	check_person_human_minimal_bounding = fields.Char('Cuadro delimitador (T,L,W,H)', default='0.0,0.0,0.0,0.0')
	check_text_identification_number = fields.Boolean('Requerir nro de identificacion declarativo')
	check_text_names = fields.Boolean('Requerir nombres')
	# dni dorso
	check_idcards_document_passport_dni_dorso = fields.Boolean('Requerir etiqueta Id Cards|Document|Passport')
	check_idcards_document_passport_confidence_dni_dorso = fields.Float('Confianza', help='De 0 a 100')
	check_idcards_document_passport_minimal_bounding_dni_dorso = fields.Char('Cuadro delimitador (T,L,W,H)', default='0.0,0.0,0.0,0.0')
	company_id = fields.Many2one('res.company', 'Empresa')
