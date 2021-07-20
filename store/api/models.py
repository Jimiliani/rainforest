from django.db import models, transaction
from django.db.models import Sum, F, OuterRef
from rest_framework.exceptions import ValidationError

from api.validators import validate_min_amount_of_items_in_orders
from user_backends import models as user_models


class Item(models.Model):
    name = models.CharField(max_length=200)
    prime_cost = models.PositiveIntegerField(default=0)
    cost = models.PositiveIntegerField(default=0)
    amount = models.PositiveIntegerField(default=0)
    returned_amount = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    owner = models.ForeignKey(user_models.User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, blank=True, through="ItemInOrderRelationship", related_name='orders')
    paid = models.BooleanField(default=False)
    sold_for = models.PositiveIntegerField(null=True)

    def pay(self, user):
        total_price = self.total_price
        if user.balance >= total_price:
            with transaction.atomic():
                user.balance -= total_price
                user.save()
                self.sold_for = total_price
                self.paid = True
                self.save()
        else:
            raise ValidationError(detail="Not enough money.")

    def return_order(self, user):
        if not self.paid:
            raise ValidationError(detail="Order is not paid yet.")
        item_ids = self.items.values_list('id', flat=True)
        with transaction.atomic():
            user.balance += self.sold_for
            user.save()
            Item.objects.filter(id__in=item_ids).update(
                returned_amount=F('returned_amount') + self.items_in_order.filter(order=self, item_id=OuterRef('id'))
            )
            self.delete()

    def __str__(self):
        return "Order #{id} of {owner}".format(id=str(self.id), owner=str(self.owner))

    @property
    def total_price(self):
        return self.items.all().aggregate(total_price=Sum('cost')).only('total_price').total_price


class ItemInOrderRelationship(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items_in_order')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orders_with_item')
    amount = models.PositiveSmallIntegerField(validators=[validate_min_amount_of_items_in_orders, ])

    def book_items(self, item, *args, **kwargs):
        with transaction.atomic():
            try:
                item.amount -= self.amount
                item.save()
                ret = super(ItemInOrderRelationship, self).save(*args, **kwargs)
            except Exception:  # FIXME
                raise ValidationError("Not enough items '{item}' for creating order.".format(item=str(self.item)))
        return ret

    def unbook_items(self, item, *args, **kwargs):
        with transaction.atomic():
            item.amount += self.amount
            item.save()
            ret = super(ItemInOrderRelationship, self).delete(*args, **kwargs)
        return ret

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.order.paid:
            raise ValidationError("Unable to change paid order")
        if not self.pk:
            return self.book_items(self.item, force_insert, force_update, using, update_fields)
        return super(ItemInOrderRelationship, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.item:
            return self.unbook_items(self.item, using, keep_parents)
        return super(ItemInOrderRelationship, self).delete(using, keep_parents)
