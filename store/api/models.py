from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=200)
    prime_cost = models.PositiveIntegerField()
    cost = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()

    def __str__(self):
        return self.name
