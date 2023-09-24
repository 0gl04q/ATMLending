from django.db import models


class Info(models.Model):
    fio = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    company = models.CharField(max_length=100)
    email = models.EmailField()
    link = models.URLField()

    def __str__(self):
        return f'{self.fio} - {self.email}'

    def save(self, *args, **kwargs):
        self.link = self.__create_link()
        super().save(*args, **kwargs)

    def __create_link(self):
        return abs(hash(f'{self.fio}+{self.email}'))
