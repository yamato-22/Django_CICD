from rest_framework import serializers
from logistic.models import Product, StockProduct, Stock


class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
    class Meta:
        model = Product
        fields = '__all__'


class ProductPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        for position in positions:
            product = position.pop('product')
            quantity = position.pop('quantity')
            price = position.pop('price')
            StockProduct.objects.create(
                stock=stock, product=product, quantity=quantity, price=price
            )

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        # Обновляем связанные таблицы:
        # Удаляем старые позиции
        old_positions = StockProduct.objects.filter(stock=instance)
        old_position_ids = set(old_positions.values_list('id', flat=True))

        # Обрабатываем новые позиции
        for position in positions:
            product = position.pop('product')
            quantity = position.pop('quantity')
            price = position.pop('price')

            # Проверяем, существует ли такая позиция
            pos = old_positions.filter(product=product).first()
            if pos:
                pos.quantity = quantity
                pos.price = price
                pos.save()
                old_position_ids.remove(pos.id)
            else:
                StockProduct.objects.create(
                    stock=instance,
                    product=product,
                    quantity=quantity,
                    price=price
                )

        # Удаляем устаревшие позиции
        StockProduct.objects.filter(id__in=old_position_ids).delete()
        return instance
