# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.exceptions import UserError, ValidationError
import boto3
import base64

class ExtendsResPartner(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	rekognition_last_update = fields.Datetime('Rekognition ultima actualizacion')
	rekognition_dni_frontal_result_ids = fields.One2many('financiera.rekognition.result', 'rekognition_dni_frontal_id', 'Resultados')
	rekognition_dni_frontal_label_ids = fields.One2many('financiera.rekognition.result.label', 'dni_frontal_id', "Etiquetas")
	rekognition_dni_frontal_text_ids = fields.One2many('financiera.rekognition.result.text', 'dni_frontal_id', "Textos")
	rekognition_dni_frontal_result = fields.Selection([('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], 'Rekognition - DNI frontal resultado')
	# dni posterior
	rekognition_dni_posterior_result_ids = fields.One2many('financiera.rekognition.result', 'rekognition_dni_posterior_id', 'Resultados')
	rekognition_dni_posterior_label_ids = fields.One2many('financiera.rekognition.result.label', 'dni_posterior_id', "Etiquetas")
	rekognition_dni_posterior_text_ids = fields.One2many('financiera.rekognition.result.text', 'dni_posterior_id', "Textos")
	rekognition_dni_posterior_result = fields.Selection([('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], 'Rekognition - DNI posterior resultado')

	def rekognition_dni_frontal_detect_labels(self, client):
		rekognition_id = self.company_id.rekognition_id
		result_dict = {}
		image = base64.b64decode(self.app_dni_frontal)
		response = client.detect_labels(Image={'Bytes': image})
		check_idcards_document_passport = False
		max_idcards_document_passport_confidence = 0
		check_person_human = False
		max_person_human_confidence = 0
		labels = []
		for label in response['Labels']:
			label_name = label['Name']
			confidence = float(label['Confidence'])
			# instances = ''
			# for instance in label['Instances']:
			# 	print ("  Bounding box")
			# 	t = float(instance['BoundingBox']['Top'])
			# 	l = float(instance['BoundingBox']['Left'])
			# 	w = float(instance['BoundingBox']['Width'])
			# 	h = float(instance['BoundingBox']['Height'])
			# 	if len(instances) > 0:
			# 		instances += '::'
			# 	instances += 'T='+str(t)+':L='+str(l)+':W='+str(w)+':H='+str(h)
			l_values =  {
				'label': label_name,
				'confidence': confidence,
			}
			labels.append((0,0, l_values))
			if label_name in ('Id Cards','Document','Passport'):
				check_idcards_document_passport = True
				max_idcards_document_passport_confidence = max(max_idcards_document_passport_confidence, confidence)
			if label_name in ('Person','Human'):
				check_person_human = True
				max_person_human_confidence = max(max_person_human_confidence, confidence)
		result = 'aprobado'
		description = ''
		if rekognition_id.check_idcards_document_passport:
			if not check_idcards_document_passport:
				result = 'rechazado'
				description += 'Parece no ser un Id Card, document o passport. '
			if rekognition_id.check_idcards_document_passport and rekognition_id.check_idcards_document_passport_confidence > 0:
				if max_idcards_document_passport_confidence < rekognition_id.check_idcards_document_passport_confidence:
					result = 'rechazado'
					description += 'No cumple la confinaza minima de ser Id Card, document o passport. '
		if rekognition_id.check_person_human:
			if not check_person_human:
				result = 'rechazado'
				description += 'Parece no tener una persona o human. '
			if rekognition_id.check_person_human and rekognition_id.check_person_human_confidence > 0:
				if max_person_human_confidence < rekognition_id.check_person_human_confidence:
					result = 'rechazado'
					description += 'No cumple la confinaza minima de incluir person o human. '
		result_dict = {
			'rekognition_dni_frontal_id': self.id,
			'image': self.app_dni_frontal,
			'rekognition_type': 'detect_labels',
			'label_ids': labels,
			'result': result,
			'description': description,
		}
		result_id = self.env['financiera.rekognition.result'].create(result_dict)
		self.rekognition_dni_frontal_label_ids = result_id.label_ids
		return result_id
	
	def rekognition_dni_frontal_detect_text(self, client):
		rekognition_id = self.company_id.rekognition_id
		result_dict = {}
		image = base64.b64decode(self.app_dni_frontal)
		response = client.detect_text(Image={'Bytes': image})
		check_text_identification_number = False
		declarative_identificaction = self.app_documento
		if not declarative_identificaction:
			declarative_identificaction = self.dni
			if not declarative_identificaction:
				raise ValidationError("No esta cargado la identificacion declarativa del cliente.")
		declarative_identificaction_with_dot = ''
		if self.app_documento and self.app_documento.isdigit():
			declarative_identificaction_with_dot = '{:,}'.format(int(self.app_documento)).replace(',', '.')
		print("Doc:: ", declarative_identificaction, declarative_identificaction_with_dot)
		names = self.name.split(' ')
		print("Nombres:: ", names)
		texts = []
		for text in response['TextDetections']:
			text_detectcion = text['DetectedText']
			confidence = float(text['Confidence'])
			if declarative_identificaction in text_detectcion:
				check_text_identification_number = True
			if declarative_identificaction_with_dot in text_detectcion:
				check_text_identification_number = True
			for name in names:
				if name in text_detectcion:
					names.remove(name)
			l_values =  {
				'text': text_detectcion,
				'confidence': confidence,
			}
			texts.append((0,0, l_values))
		result = 'aprobado'
		description = ''
		if rekognition_id.check_text_identification_number:
			if not check_text_identification_number:
				result = 'rechazado'
				nro_buscados = str(declarative_identificaction)
				if len(declarative_identificaction_with_dot) > 0:
					nro_buscados += ' y/o ' + declarative_identificaction_with_dot
				description = nro_buscados + ' no encontrada en imagen. '
		if rekognition_id.check_text_names:
			for name in names:
				result = 'rechazado'
				description += name + ' no encontrado en la imagen. '
		result_dict = {
			'rekognition_dni_frontal_id': self.id,
			'image': self.app_dni_frontal,
			'rekognition_type': 'detect_text',
			'text_ids': texts,
			'result': result,
			'description': description,
		}
		result_id = self.env['financiera.rekognition.result'].create(result_dict)
		self.rekognition_dni_frontal_text_ids = result_id.text_ids
		return result_id

	@api.one
	def rekognition_dni_frontal(self):
		rekognition_id = self.company_id.rekognition_id
		if self.app_dni_frontal:
			client=boto3.client(
				'rekognition',
				region_name=rekognition_id.region,
				aws_access_key_id = rekognition_id.id_access_key,
				aws_secret_access_key = rekognition_id.secret_access_key,
			)
			result_labels_id = self.rekognition_dni_frontal_detect_labels(client)
			self.rekognition_last_update = datetime.now()
			if result_labels_id.result == 'aprobado':
				result_text_id = self.rekognition_dni_frontal_detect_text(client)
				if result_labels_id.result == 'aprobado' and result_text_id.result == 'aprobado':
					self.rekognition_dni_frontal_result = 'aprobado'
				else:
					self.rekognition_dni_frontal_result = 'rechazado'
			else:
				self.rekognition_dni_frontal_result = 'rechazado'


	def rekognition_dni_posterior_detect_labels(self, client):
		rekognition_id = self.company_id.rekognition_id
		result_dict = {}
		image = base64.b64decode(self.app_dni_posterior)
		response = client.detect_labels(Image={'Bytes': image})
		check_idcards_document_passport_dni_dorso = False
		max_idcards_document_passport_confidence_dni_dorso = 0
		check_person_human = False
		max_person_human_confidence = 0
		labels = []
		for label in response['Labels']:
			label_name = label['Name']
			confidence = float(label['Confidence'])
			# instances = ''
			# for instance in label['Instances']:
			# 	print ("  Bounding box")
			# 	t = float(instance['BoundingBox']['Top'])
			# 	l = float(instance['BoundingBox']['Left'])
			# 	w = float(instance['BoundingBox']['Width'])
			# 	h = float(instance['BoundingBox']['Height'])
			# 	if len(instances) > 0:
			# 		instances += '::'
			# 	instances += 'T='+str(t)+':L='+str(l)+':W='+str(w)+':H='+str(h)
			l_values =  {
				'label': label_name,
				'confidence': confidence,
			}
			labels.append((0,0, l_values))
			if label_name in ('Id Cards','Document','Passport'):
				check_idcards_document_passport_dni_dorso = True
				max_idcards_document_passport_confidence_dni_dorso = max(max_idcards_document_passport_confidence_dni_dorso, confidence)
			if label_name in ('Person','Human'):
				check_person_human = True
				max_person_human_confidence = max(max_person_human_confidence, confidence)
		result = 'aprobado'
		description = ''
		if rekognition_id.check_idcards_document_passport_dni_dorso:
			if not check_idcards_document_passport_dni_dorso:
				result = 'rechazado'
				description += 'Parece no ser un Id Card, document o passport. '
			if rekognition_id.check_idcards_document_passport_dni_dorso and rekognition_id.check_idcards_document_passport_confidence_dni_dorso > 0:
				if max_idcards_document_passport_confidence_dni_dorso < rekognition_id.check_idcards_document_passport_confidence_dni_dorso:
					result = 'rechazado'
					description += 'No cumple la confinaza minima de ser Id Card, document o passport. '
		# if rekognition_id.check_person_human:
		# 	if not check_person_human:
		# 		result = 'rechazado'
		# 		description += 'Parece no tener una persona o human. '
		# 	if rekognition_id.check_person_human and rekognition_id.check_person_human_confidence > 0:
		# 		if max_person_human_confidence < rekognition_id.check_person_human_confidence:
		# 			result = 'rechazado'
		# 			description += 'No cumple la confinaza minima de incluir person o human. '
		result_dict = {
			'rekognition_dni_posterior_id': self.id,
			'image': self.app_dni_posterior,
			'rekognition_type': 'detect_labels',
			'label_ids': labels,
			'result': result,
			'description': description,
		}
		result_id = self.env['financiera.rekognition.result'].create(result_dict)
		self.rekognition_dni_posterior_label_ids = result_id.label_ids
		self.rekognition_last_update = datetime.now()
		return result_id
	
	def rekognition_dni_posterior_detect_text(self, client):
		rekognition_id = self.company_id.rekognition_id
		result_dict = {}
		image = base64.b64decode(self.app_dni_posterior)
		response = client.detect_text(Image={'Bytes': image})
		check_text_identification_number = False
		declarative_identificaction = self.app_documento
		if not declarative_identificaction:
			declarative_identificaction = self.dni
			if not declarative_identificaction:
				raise ValidationError("No esta cargado la identificacion declarativa del cliente.")
		declarative_identificaction_with_dot = ''
		if self.app_documento and self.app_documento.isdigit():
			declarative_identificaction_with_dot = '{:,}'.format(int(self.app_documento)).replace(',', '.')
		print("Doc:: ", declarative_identificaction, declarative_identificaction_with_dot)
		names = self.name.split(' ')
		print("Nombres:: ", names)
		texts = []
		for text in response['TextDetections']:
			text_detectcion = text['DetectedText']
			confidence = float(text['Confidence'])
			if declarative_identificaction in text_detectcion:
				check_text_identification_number = True
			if declarative_identificaction_with_dot in text_detectcion:
				check_text_identification_number = True
			for name in names:
				if name in text_detectcion:
					names.remove(name)
			l_values =  {
				'text': text_detectcion,
				'confidence': confidence,
			}
			texts.append((0,0, l_values))
		result = 'aprobado'
		description = ''
		# if rekognition_id.check_text_identification_number:
		# 	if not check_text_identification_number:
		# 		result = 'rechazado'
		# 		nro_buscados = str(declarative_identificaction)
		# 		if len(declarative_identificaction_with_dot) > 0:
		# 			nro_buscados += ' y/o ' + declarative_identificaction_with_dot
		# 		description = nro_buscados + ' no encontrada en imagen. '
		# if rekognition_id.check_text_names:
		# 	for name in names:
		# 		result = 'rechazado'
		# 		description += name + ' no encontrado en la imagen. '
		result_dict = {
			'rekognition_dni_posterior_id': self.id,
			'image': self.app_dni_posterior,
			'rekognition_type': 'detect_text',
			'text_ids': texts,
			'result': result,
			'description': description,
		}
		result_id = self.env['financiera.rekognition.result'].create(result_dict)
		self.rekognition_dni_posterior_text_ids = result_id.text_ids
		return result_id

	@api.one
	def rekognition_dni_posterior(self):
		rekognition_id = self.company_id.rekognition_id
		if self.app_dni_posterior:
			client=boto3.client(
				'rekognition',
				region_name=rekognition_id.region,
				aws_access_key_id = rekognition_id.id_access_key,
				aws_secret_access_key = rekognition_id.secret_access_key,
			)
			result_labels_id = self.rekognition_dni_posterior_detect_labels(client)
			self.rekognition_last_update = datetime.now()
			if result_labels_id.result == 'aprobado':
				self.rekognition_dni_posterior_result = 'aprobado'
			else:
				self.rekognition_dni_posterior_result = 'rechazado'

class FinancieraRekognitionResult(models.Model):
	_name = 'financiera.rekognition.result'

	_order = 'id desc'
	rekognition_dni_frontal_id = fields.Many2one('res.partner', 'Cliente')
	rekognition_dni_posterior_id = fields.Many2one('res.partner', 'Cliente')
	# rekognition_selfie_id = fields.Many2one('res.partner', 'Cliente')
	
	image = fields.Binary('Imagen')
	imagen2 = fields.Binary('Imagen de referencia')
	label_ids = fields.One2many('financiera.rekognition.result.label', 'result_id', "Etiquetas")
	text_ids = fields.One2many('financiera.rekognition.result.text', 'result_id', "Textos")
	rekognition_type = fields.Selection([('detect_labels', 'Detect labels'), ('detect_text', 'Detect text')], 'Tipo de reconocimiento')
	result = fields.Selection([('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], 'Resultado')
	description = fields.Char("Descripcion")

class FinancieraRekognitionResultLabel(models.Model):
	_name = 'financiera.rekognition.result.label'

	result_id = fields.Many2one('financiera.rekognition.result', 'Resultado')
	dni_frontal_id = fields.Many2one('res.partner', 'Cliente')
	dni_posterior_id = fields.Many2one('res.partner', 'Cliente')
	label = fields.Char("Etiqueta")
	confidence = fields.Float('Confianza', digits=(16,2))

class FinancieraRekognitionResultText(models.Model):
	_name = 'financiera.rekognition.result.text'

	result_id = fields.Many2one('financiera.rekognition.result', 'Resultado')
	dni_frontal_id = fields.Many2one('res.partner', 'Cliente')
	dni_posterior_id = fields.Many2one('res.partner', 'Cliente')
	text = fields.Char("Texto")
	confidence = fields.Float('Confianza', digits=(16,2))