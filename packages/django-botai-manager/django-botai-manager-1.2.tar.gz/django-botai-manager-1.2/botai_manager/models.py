from django.db import models


class Company(models.Model):
	name			= models.CharField(max_length=100, null=False)
	creation_date	= models.DateTimeField(auto_now_add=True)
	enable 			= models.BooleanField(default=True)

	class Meta:
		db_table    =   'company'
		managed     =   True

	@classmethod
	def get_company_by_id(cls, company_id):
		return cls.objects.filter(id=company_id).order_by('id').get()
