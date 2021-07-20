from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=200)
    prime_cost = models.PositiveIntegerField(default=0)
    cost = models.PositiveIntegerField(default=0)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
