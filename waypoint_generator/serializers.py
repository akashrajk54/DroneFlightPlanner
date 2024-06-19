from rest_framework import serializers
from .models import FlightPath


class FlightPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightPath
        fields = '__all__'

    def validate(self, data):
        if len(data['polygon_lat_lon']) < 3:
            raise serializers.ValidationError("Polygon must have at least 3 points and must be closed.")
        if data['altitude'] < 100:
            raise serializers.ValidationError("Altitude must be at least 100 meters.")
        if data['overlapping_percentage'] < 50:
            raise serializers.ValidationError("Image overlapping percentage must be at least 50%.")
        return data
