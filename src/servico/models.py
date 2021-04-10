from django.db import models
from django.utils.text import slugify


class EquipeAtendimento(models.Model):
    nome = models.CharField(
        db_index=True,
        max_length=20,
        )
    slug = models.SlugField()
    descricao = models.CharField(
        'Descrição',
        max_length=250,
        null=True,
        blank=True,
        )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'fo2_serv_equipe'
        verbose_name = 'Equipe de atendimento'
        verbose_name_plural = 'Equipes de atendimento'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        if not self.descricao:
            self.descricao = self.nome
        super(EquipeAtendimento, self).save(*args, **kwargs)


