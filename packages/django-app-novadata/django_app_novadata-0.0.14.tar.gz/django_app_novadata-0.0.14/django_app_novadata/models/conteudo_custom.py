from django.db import models


class ConteudoCustom(models.Model):
    '''
    A classe ConteudoCustom serve para armazernar os(as) Conteúdos customizados do sistema.
    Além de fazer as implementações relacionadas a um único objeto do tipo ConteudoCustom.
    '''
    LOCAL_CHOICES = (
        ('Nenhum Local','Nenhum Local'),
        ('Head - Admin','Head - Admin'),
        ('Style - Admin', 'Style - Admin'),
        ('Script - Admin','Script - Admin'),
    )

    local = models.CharField(
        verbose_name='',
        max_length=100,
        choices=LOCAL_CHOICES,
        default='Nenhum Local',

    )

    conteudo = models.TextField(
        verbose_name="Conteúdo",
        null=True
    )

    def __str__(self):
        return self.local

    class Meta:
        app_label = 'django_app_novadata'
        verbose_name = 'Conteúdo Customizado'
        verbose_name_plural = 'Conteúdos Customizados'
